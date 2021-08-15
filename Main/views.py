from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from Main.models import UserInfo, Product, Shop
from django.http import JsonResponse
import json
import random
from modules import dashboard
from datetime import datetime, date

# Create your views here.


def register(request):
    if request.method == "POST":
        user1 = User.objects.filter(username=request.POST.get(
            "username"))
        user2 = User.objects.filter(email=request.POST.get(
            "email"))
        if len(user1) == 0 and len(user2) == 0:
            user = User.objects.create_user(username=request.POST.get(
                "username"), password=request.POST.get("password"))
            user.first_name = request.POST.get("fullname")
            user.email = request.POST.get("email")
            user.is_superuser = False
            user.save()
            messages.info(
                request, 'You are registered successfully. Please Login to continue.')
            return render(request, "login.html")
        else:
            messages.warning(
                request, 'Username or E-Mail already taken. Please Sign Up using another username.')
            return render(request, "login.html")
    elif not request.user.is_anonymous:
        return redirect("/home")
    else:
        return render(request, "login.html")


def loginUser(request):
    if request.method == "POST":
        name = request.POST.get(
            "username")
        user = authenticate(
            username=name, password=request.POST.get("password"))
        if user is not None:
            login(request, user)
            userchoice = UserInfo.objects.filter(username=request.user.id)
            if len(userchoice):
                userchoice = UserInfo.objects.get(username=request.user.id)
                userchoice.visitedSite += 1
                userchoice.save()
                return redirect("/home")
            else:
                return render(request, "person.html")
        else:
            # No backend authenticated the credentials
            messages.warning(
                request, 'Wrong Username or Password.')
            return render(request, "login.html")
    elif not request.user.is_anonymous:
        userchoice = UserInfo.objects.filter(username=request.user.id)
        if len(userchoice):
            userchoice = UserInfo.objects.get(username=request.user.id)
            userchoice.visitedSite += 1
            userchoice.save()
            return redirect("/home")
        else:
            return render(request, "person.html")
    else:
        return render(request, "login.html")


def logoutUser(request):
    logout(request)
    messages.info(
        request, 'You Logout Successfully. Come back soon.')
    return redirect("/login")


def home(request):
    if request.user.is_anonymous:
        return redirect("/login")
    userIn = UserInfo.objects.filter(username=request.user)
    if len(userIn) == 0:
        return render(request, "person.html")
    isShop = False
    # button = {}
    # dashboard.dashboard(10,20,30)
    userIn = UserInfo.objects.get(username=request.user)
    typeOf = userIn.typeOf
    userShop = Shop.objects.filter(username=request.user)
    if len(userShop):
        isShop = True

    context = {
        "isShop": isShop,
        "typeOf": typeOf,
    }
    return render(request, "index.html", context)


def ajaxStartupDetails(request):
    if request.user.is_anonymous:
        value = "false"
    # print(request.user)
    username = request.user
    typeOf = request.POST.get('typeOf', None)
    gender = request.POST.get('gender', None)
    categories = request.POST.get('category', None)
    userchoice = UserInfo.objects.filter(username=username)
    if len(userchoice):
        value = "already"
    else:
        userD = UserInfo(username=username, gender=gender,
                         categories=categories, typeOf=typeOf)
        userD.save()
        value = "true"
    data1 = {
        'successful': value,
    }

    return JsonResponse(data1, safe=False)


def profile(request):
    if request.user.is_anonymous:
        return redirect("/login")
    profile = {}
    userInfo = UserInfo.objects.get(username=request.user)
    userUp = User.objects.get(username=request.user)
    profile["username"] = request.user
    profile["email"] = userUp.email
    name = userUp.get_full_name().split()
    profile["firstName"] = name[0]
    if len(name) > 1:
        profile["lastName"] = name[1]
    typeOf = userInfo.typeOf
    profile["address"] = userInfo.addressPrimary
    profile["city"] = userInfo.city
    profile["state"] = userInfo.state
    profile["postal"] = userInfo.postal
    profile["about"] = userInfo.about
    profile["wishlist"] = len(userInfo.cart.split(
        ",")) if userInfo.cart != "" else 0
    profile["cart"] = len(userInfo.cart.split(
        ",")) if userInfo.cart != "" else 0
    profile["visited"] = userInfo.visitedSite
    context = {
        "profile": profile,
        "typeOf": typeOf,
    }

    return render(request, "myprofile.html", context)


def profileEdit(request):
    if request.user.is_anonymous:
        value = "false"
    # print(request.user)
    first = request.POST.get('first', None)
    last = request.POST.get('last', None)
    address = request.POST.get('address', None)
    city = request.POST.get('city', None)
    state = request.POST.get('state', None)
    postal = request.POST.get('postal', None)
    about = request.POST.get('about', None)

    userInfo = UserInfo.objects.get(username=request.user)
    userUp = User.objects.get(username=request.user)

    userUp.first_name = first
    userUp.last_name = last
    userInfo.addressPrimary = address
    userInfo.postal = postal
    userInfo.city = city
    userInfo.state = state
    userInfo.about = about

    userInfo.save()
    userUp.save()
    value = "true"
    data1 = {
        'successful': value,
    }

    return JsonResponse(data1, safe=False)


def cart(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "wholeseller":
        return redirect("/login")
    userCart = UserInfo.objects.filter(username=request.user)
    products = []
    if len(userCart):
        data = {}
        inCart = userCart[0].cart
        if inCart:
            inCart = inCart.split(",")[:-1]
            for item in inCart:
                data = {}
                data["productId"], data["quantity"] = item.split(":;:")
                try:
                    userProduct = Product.objects.get(
                        productId=data['productId'])
                    data["productName"] = userProduct.productName
                    data["selling"] = userProduct.sellingPrice
                    data["category"] = userProduct.category
                    data["image"] = userProduct.image1
                    products.append(data)
                except:
                    userItemDelete = UserInfo.objects.get(
                        username=request.user)
                    userItemDelete.cart = userItemDelete.cart.replace(
                        item + ",", "")
                    userItemDelete.save()

        context = {
            "data": products,
            "typeOf": typeOf,
        }

    return render(request, "mycart.html", context)


def shop(request, productUrl):
    if request.user.is_anonymous:
        return redirect("/login")
    isOwner = False
    shopId = User.objects.get(username=productUrl)
    userId = shopId.id
    userFilter = Shop.objects.filter(username=userId)
    if len(userFilter):
        shop = {}
        userShop = Shop.objects.get(username=userId)
        shop['username'] = productUrl
        shop['shopName'] = userShop.shopName
        cat = userShop.categories.split(",")
        shop["categoriesButton"] = cat
        shop['owner'] = userShop.owner
        shop['address'] = userShop.addressPrimary
        shop['contact'] = userShop.contact
        shop['city'] = userShop.city
        shop['state'] = userShop.state
        shop['postal'] = userShop.postal
        shop['description'] = userShop.description
        image1 = userShop.image1
        image2 = userShop.image2
        image3 = userShop.image3
        shop['images'] = [{"value": 0, "image": image1}, {
            "value": 1, "image": image2}, {"value": 2, "image": image3}]
        userData = UserInfo.objects.get(username=request.user)
        shopVisited = userData.shopVisited

        if productUrl not in shopVisited:
            userData.productVisited = shopVisited + \
                productUrl + ":;:" + str(1) + ","
            userData.save()
        else:
            visited = shopVisited.split(",")
            for item in visited[:-1]:
                if productUrl in item:
                    old = item
                    qty = int(item.split(":;:")[1]) + 1
                    new = productUrl + ":;:" + str(qty)
                    userData. shopVisited = shopVisited.replace(old, new)
                    userData.save()

            items = []
            for item in cat:
                val = {}
                if item == "men":
                    val["image"] = "img/menswear.jpg"
                    val["name"] = item
                    val["url"] = productUrl + "-" + item
                    items.append(val)
                elif item == "women":
                    val["image"] = "img/womenswear.jpg"
                    val["name"] = item
                    val["url"] = productUrl + "-" + item
                    items.append(val)
                elif item == "footwear":
                    val["image"] = "img/shoeswear.jpg"
                    val["name"] = item
                    val["url"] = productUrl + "-" + item
                    items.append(val)
                elif item == "pharmacy":
                    val["image"] = "img/pharmacy.jpg'", item
                    val["name"] = item
                    val["url"] = productUrl + "-" + item
                    items.append(val)
                else:
                    val["image"] = "img/homedecor.jpg", item
                    val["name"] = item
                    val["url"] = productUrl + "-" + item
                    items.append(val)

            shop["categories"] = items

        if str(request.user) == productUrl:
            isOwner = True
        else:
            userShop.totalVisited += 1
            userShop.save()

        context = {
            "userIsOwner": isOwner,
            "shop": shop,
            "typeOf": typeOfUser(request.user),
        }
        return render(request, "shop.html", context)
    return redirect("/home")


def createShop(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "customer":
        return redirect("/login")
    userIn = UserInfo.objects.get(username=request.user)
    typeOf = userIn.typeOf
    if typeOf == "customer":
        return redirect("/home")
    userFilter = Shop.objects.filter(username=request.user)
    if len(userFilter):
        return redirect("/home")
    categories = userIn.categories.split(",")
    context = {
        "categories": categories,
        "typeOf": typeOf,
    }
    return render(request, "createShop.html", context)


def editShop(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "customer":
        return redirect("/login")
    userFilter = Shop.objects.filter(username=request.user)
    if len(userFilter):
        totalCategories = ["men", "women", "footwear", "pharmacy"]
        shop = {}
        userShop = Shop.objects.get(username=request.user)
        shop['shopName'] = userShop.shopName
        shop['categoriesNormal'] = userShop.categories
        cat = shop['categoriesNormal'].split(",")
        shop["categoriesButton"] = cat
        shop['owner'] = userShop.owner
        shop['address'] = userShop.addressPrimary
        shop['contact'] = userShop.contact
        shop['city'] = userShop.city
        shop['state'] = userShop.state
        shop['postal'] = userShop.postal
        shop['description'] = userShop.description

        items = []
        for item in totalCategories:
            val = {}
            if item in cat:
                val["tag"] = "checked"
                val["name"] = item
                items.append(val)
            else:
                val["tag"] = ""
                val["name"] = item
                items.append(val)

        shop["categories"] = items
        context = {
            "shop": shop,
            "typeOf": typeOfUser(request.user),
        }
    return render(request, "editpage.html", context)


def submitShop(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "customer":
        return redirect("/login")
    if request.method == "POST":
        userFilter = Shop.objects.filter(username=request.user)
        if len(userFilter) < 1:
            username = request.user
            shopName = request.POST.get("shopName")
            category = request.POST.get("categoryName")
            owner = request.POST.get("owner")
            address = request.POST.get("address")
            contact = request.POST.get("contact")
            city = request.POST.get("city")
            state = request.POST.get("state")
            postal = request.POST.get("postal")
            desc = request.POST.get("desc")
            image1 = request.FILES.get("image1")
            image2 = request.FILES.get("image2")
            image3 = request.FILES.get("image3")

            userIn = UserInfo.objects.get(username=request.user)
            typeOf = userIn.typeOf

            userData = Shop(username=username, typeOf=typeOf, shopName=shopName, categories=category, description=desc, owner=owner,
                            addressPrimary=address, contact=contact, city=city, state=state, postal=postal, image1=image1, image2=image2, image3=image3)
            userData.save()
            return redirect("/home")

    return redirect("/home")


def updateShop(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "customer":
        return redirect("/login")
    if request.method == "POST":
        userFilter = Shop.objects.filter(username=request.user)
        if len(userFilter):
            userData = userFilter[0]
            userData.image1.delete()
            userData.image2.delete()
            userData.image3.delete()
            userData.save()
            userData = userFilter[0]
            userData.categories = request.POST.get("categoryName")
            userData.addressPrimary = request.POST.get("address")
            userData.contact = request.POST.get("contact")
            userData.city = request.POST.get("city")
            userData.state = request.POST.get("state")
            userData.postal = request.POST.get("postal")
            userData.description = request.POST.get("desc")
            userData.image1 = request.FILES.get("image1")
            userData.image2 = request.FILES.get("image2")
            userData.image3 = request.FILES.get("image3")
            userData.save()

    return redirect("/home")


def createProduct(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "customer":
        return redirect("/login")
    userFilter = Shop.objects.filter(username=request.user)
    if len(userFilter):
        userIn = Shop.objects.get(username=request.user)
        categories = userIn.categories.split(",")
        context = {
            "categories": categories,
            "typeOf": typeOf,
        }
        return render(request, "createProduct.html", context)
    return redirect("/home")


def submitProduct(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "customer":
        return redirect("/login")
    if request.method == "POST":
        userFilter = Shop.objects.filter(username=request.user)
        if len(userFilter):
            username = request.user
            productName = request.POST.get("productName")
            category = request.POST.get("category")
            actual = int(request.POST.get("actual"))
            selling = int(request.POST.get("selling"))
            discount = request.POST.get("coupon")
            description = request.POST.get("description")
            stock = int(request.POST.get("stock"))
            image1 = request.FILES.get("image1")
            image2 = request.FILES.get("image2")
            image3 = request.FILES.get("image3")

            if (discount):
                discount = discount.lower()

            userShop = Shop.objects.get(username=request.user)
            typeOf = userShop.typeOf
            products = userShop.countId
            userShop.save()
            productId = str(username) + "-" + str(products)

            userData = Product(username=username, productName=productName, productId=productId, typeOf=typeOf, category=category, actualPrice=actual,
                               sellingPrice=selling, coupon=discount, description=description, stock=stock, image1=image1, image2=image2, image3=image3)
            userData.save()

            userShop.countId += 1
            userShop.totalProducts += 1
            userShop.totalStock += stock
            userShop.save()
            return redirect("/home")


def productSearch(request, productUrl):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "wholeseller":
        return redirect("/login")
    person = ["customer", "retailer", "wholeseller"]
    filterProduct = person[person.index(typeOf)+1]
    productUrl = productUrl.lower()
    disable = False

    if "-" in productUrl:
        productUrl = productUrl.split("-")
        username = User.objects.get(username=productUrl[0]).id
        if len(productUrl) == 2:
            prodCategory = productUrl[1]
            userData = Product.objects.filter(username=username).filter(
                category=prodCategory).filter(typeOf=filterProduct)
        else:
            userData = Product.objects.filter(
                username=username).filter(typeOf=filterProduct)
    elif productUrl in ["men", "women", "footwear", "pharmacy", "home"]:
        userData = Product.objects.all().filter(
            category=productUrl).filter(typeOf=filterProduct)
    else:
        userData = Product.objects.all().filter(typeOf=filterProduct)

    main = []
    if len(userData):
        for data in userData:
            products = {}
            products["image"] = data.image1
            products["productName"] = data.productName
            products["selling"] = data.sellingPrice
            products["actual"] = data.actualPrice
            products["id"] = data.productId
            main.append(products)

    if len(main):
        disable = True

    context = {
        "products": main,
        "disable": disable,
        "typeOf": typeOf,
    }

    return render(request, "productSearch.html", context)


def productPage(request, productUrl):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous:
        return redirect("/login")
    person = ["customer", "retailer", "wholeseller"]
    filterProduct = person[person.index(typeOf)+1]

    if productUrl.split("-")[0] == str(request.user):
        typeOf = "wholeseller"
        userData = Product.objects.get(productId=productUrl)
    else:
        userData = Product.objects.filter(
            productId=productUrl).filter(typeOf=filterProduct)

    data = {}
    if userData:
        userData = userData[0]
        data["inCart"] = False
        data["productId"] = userData.productId
        data["productName"] = userData.productName
        wishlist = UserInfo.objects.filter(username=request.user)[0].wishlist
        data["inWishlist"] = productUrl in wishlist
        data["selling"] = userData.sellingPrice
        data["actual"] = userData.actualPrice
        data["stock"] = userData.stock
        data["description"] = userData.description
        data["seller"] = userData.username
        image1 = userData.image1
        image2 = userData.image2
        image3 = userData.image3
        off = (1 - (data["selling"] / data["actual"])) * 100
        data["off"] = round(off, 2)

        data["images"] = [{"target": image1, "value": 1}, {
            "target": image2, "value": 2}, {"target": image3, "value": 3}]

        data["shopName"] = Shop.objects.get(username=data["seller"]).shopName

        if not request.user.is_anonymous:
            userCart = UserInfo.objects.get(username=request.user).cart
            if userCart:
                userCart = userCart.split(",")
                for item in userCart:
                    if data["productId"] in item:
                        data["countInCart"] = item.split(":;:")[1]
                        data["inCart"] = True

        userData.views += 1
        userData.save()
        userData = UserInfo.objects.get(username=request.user)
        productVisited = userData.productVisited

        if data["productId"] not in productVisited:
            userData.productVisited = productVisited + \
                data["productId"] + ":;:" + str(1) + ","
            userData.save()
        else:
            visited = productVisited.split(",")
            for item in visited[:-1]:
                if data["productId"] in item:
                    old = item
                    qty = int(item.split(":;:")[1]) + 1
                    new = data["productId"] + ":;:" + str(qty)
                    userData.productVisited = productVisited.replace(old, new)
                    userData.save()

        userShop = Shop.objects.get(username=data["seller"])
        productVisited = userShop.productVisited

        if data["productId"] not in productVisited:
            userShop.productVisited = productVisited + \
                data["productId"] + ":;:" + str(1) + ","
            userShop.save()
        else:
            visited = productVisited.split(",")
            for item in visited[:-1]:
                if data["productId"] in item:
                    old = item
                    qty = int(item.split(":;:")[1]) + 1
                    new = data["productId"] + ":;:" + str(qty)
                    userShop.productVisited = productVisited.replace(old, new)
                    userShop.save()

    context = {
        "data": data,
        "typeOf": typeOf,
    }
    if productUrl.split("-")[0] == str(request.user):
        return render(request, "productMain.html", context)

    elif typeOf == "wholeseller":
        return redirect("/login")

    return render(request, "productMain.html", context)


def readCart(request):
    # print(request.user)
    cartValue = "false"
    username = request.POST.get('user', None)

    if username != "AnonymousUser" or username != None:
        userCart = UserInfo.objects.get(username=username).cart.split(",")
        if len(userCart[0]):
            cartValue = "true"

    data1 = {
        'cartValue': cartValue,
    }
    return JsonResponse(data1, safe=False)


def updateCart(request):
    # print(request.user)
    completed = False
    success = "false"
    username = request.POST.get('user', None)
    productId = request.POST.get('productId', None)
    value = request.POST.get('value', None)
    if value != None:
        productString = productId + ":;:" + str(value)

        if not request.user.is_anonymous:
            userInfo = UserInfo.objects.get(username=username)
            userCart = userInfo.cart
            userCartList = userCart.split(",")

            if len(userCartList[0]):
                for item in userCartList:
                    if productId in item:
                        if not value or value == "false":
                            userCart = userCart.replace(item + ",", "")
                            completed = True
                        else:
                            userCart = userCart.replace(item, productString)
                            completed = True
                if not completed:
                    userCart += productString + ","
            else:
                userCart = productString + ","

            userInfo.cart = userCart
            userInfo.save()
            success = "true"

    data1 = {
        'success': success,
    }
    return JsonResponse(data1, safe=False)


def readWishlist(request):
    # print(request.user)
    WishlistValue = "false"
    username = request.POST.get('user', None)

    if username != "AnonymousUser" or username != None:
        userWishlist = UserInfo.objects.filter(username=username)
        if (userWishlist[0].wishlist):
            WishlistValue = "true"

    data1 = {
        'WishlistValue': WishlistValue,
    }
    return JsonResponse(data1, safe=False)


def updateWishlist(request):
    # print(request.user)
    success = "false"
    username = request.POST.get('user', None)
    name = User.objects.get(id=username).username
    option = request.POST.get('value', None)
    productId = request.POST.get('productId', None)
    owner = User.objects.get(username=productId.split("-")[0]).id

    if int(username) > 0:
        userInfo = UserInfo.objects.get(username=username)
        userWishlist = userInfo.wishlist
        shop = Shop.objects.get(username=owner)
        shopWishlist = shop.wishlisted
        product = Product.objects.get(productId=productId)
        productWish = product.wishlist
        if option == "true":

            if productId not in userWishlist:
                userWishlist = userWishlist + productId + ","
                userInfo.wishlist = userWishlist
                userInfo.save()

                if name not in shopWishlist:
                    shop.wishlisted = shopWishlist + \
                        name + ":;:" + str(1) + ","
                    shop.save()
                else:
                    wish = shopWishlist.split(",")[:-1]
                    for item in wish:
                        if name == item.split(":;:")[0]:
                            old = item
                            times = int(item.split(":;:")[1]) + 1
                            new = name + ":;:" + str(times)
                            shop.wishlisted = shopWishlist.replace(old, new)
                            shop.save()
            productWish += 1
            product.wishlist = productWish
            product.save()

            success = "true"
        else:

            if productId in userWishlist:
                userWishlist = userWishlist.replace(productId + ",", "")
                userInfo.wishlist = userWishlist
                userInfo.save()

            wish = shopWishlist.split(",")[:-1]
            for item in wish:
                if name == item.split(":;:")[0]:
                    old = item
                    times = int(item.split(":;:")[1])
                    if times > 1:
                        times = times - 1
                        new = name + ":;:" + str(times)
                        shop.wishlisted = shopWishlist.replace(old, new)
                        shop.save()
                    else:
                        new = ""
                        shop.wishlisted = shopWishlist.replace(old + ",", new)
                        shop.save()

            productWish -= 1
            product.wishlist = productWish
            product.save()
            success = "true"

    data1 = {
        'success': success,
    }
    return JsonResponse(data1, safe=False)


def wishlist(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "wholeseller":
        redirect("/login")
    products = []
    userData = UserInfo.objects.get(username=request.user)
    wishlist = userData.wishlist
    userWish = wishlist.split(",")[:-1]
    if len(userWish):
        for product in userWish:
            data = {}
            userProduct = Product.objects.filter(productId=product)
            if len(userProduct):
                productDetail = userProduct[0]
                data["productId"] = product
                data["productName"] = productDetail.productName
                data["category"] = productDetail.category
                data["selling"] = productDetail.sellingPrice
                data["image"] = productDetail.image1
                owner = product.split("-")[0]
                ownerId = User.objects.get(username=owner).id
                data["shopName"] = Shop.objects.filter(
                    username=ownerId)[0].shopName
                products.append(data)
            else:
                wishlist = wishlist.replace(product + ",", "")

    context = {
        "data": products,
        "typeOf": typeOf,
    }

    return render(request, "myWishlist.html", context)


def myProducts(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "customer":
        return redirect("/login")
    data = []
    userIn = request.user
    userCheck = Shop.objects.filter(username=userIn)

    if len(userCheck):
        userData = Product.objects.filter(username=userIn)
        for product in userData:
            prod = {}
            prod["productId"] = product.productId
            prod["productName"] = product.productName
            prod["image"] = product.image1
            prod["stock"] = product.stock
            prod["wishlist"] = product.wishlist
            prod["buyed"] = product.buyed
            prod["views"] = product.views
            data.append(prod)

    context = {
        "data": data,
        "typeOf": typeOf,
    }
    return render(request, "myProducts.html", context)


def editProduct(request, productId):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "customer":
        return redirect("/login")
    data = {}
    userData = Product.objects.filter(productId=productId)
    if len(userData):
        user = userData[0].username
        if user == request.user:
            userData = userData[0]
            data["productId"] = productId
            data["productName"] = userData.productName
            data["category"] = userData.category
            data["actual"] = userData.actualPrice
            data["selling"] = userData.sellingPrice
            data["discount"] = userData.coupon
            data["description"] = userData.description
            data["stock"] = userData.stock
            data["categories"] = Shop.objects.get(
                username=user).categories.split(",")
            data["categories"].remove(data["category"])
            context = {
                "data": data,
                "typeOf": typeOf,
            }
            return render(request, "editProduct.html", context)
    return redirect("/home")


def updateProduct(request, productIdIn):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "customer":
        return redirect("/login")
    if request.method == "POST":
        userFilter = Product.objects.filter(productId=productIdIn)
        if len(userFilter):
            userData = userFilter[0]
            userData.image1.delete()
            userData.image2.delete()
            userData.image3.delete()
            userData.save()
            userData = userFilter[0]
            userData.category = request.POST.get("category")
            userData.productName = request.POST.get("productName")
            userData.actualPrice = request.POST.get("actual")
            userData.sellingPrice = request.POST.get("selling")
            userData.stock = request.POST.get("stock")
            userData.description = request.POST.get("description")
            userData.coupon = request.POST.get("discount")
            userData.image1 = request.FILES.get("image1")
            userData.image2 = request.FILES.get("image2")
            userData.image3 = request.FILES.get("image3")
            userData.save()

    return redirect("/home")


def search(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "wholeseller":
        return redirect("/login")
    person = ["customer", "retailer", "wholeseller"]
    filterProduct = person[person.index(typeOf)+1]
    searchText = request.GET.get("searchName")
    products = Product.objects.all().filter(typeOf=filterProduct)
    shops = Shop.objects.all().filter(typeOf=filterProduct)
    isDisable = False
    if searchText.lower() == "all":
        productMain = []
        for data in products:
            products = {}
            products["image"] = data.image1
            products["productName"] = data.productName
            products["selling"] = data.sellingPrice
            products["actual"] = data.actualPrice
            products["id"] = data.productId
            productMain.append(products)
        shopMain = []
        for data in shops:
            shop = {}
            shop["image"] = data.image1
            shop["shopName"] = data.shopName
            shop["owner"] = data.owner
            shop["categories"] = data.categories
            shop["id"] = data.username
            shopMain.append(shop)
    else:
        searchText = searchText.split()
        productDict = {}
        shopDict = {}

        for product in products:
            count = 0
            name = product.productName.lower()
            productDesc = product.description.lower()
            productCat = product.category.lower()
            productId = product.productId
            for text in searchText:
                if (text in name) or (text in productDesc) or (text in productCat):
                    count += 1
            if count > 0:
                productDict[productId] = count

        sortedId = sorted(productDict, key=productDict.get)  # [1, 3, 2]

        productMain = []
        for code in sortedId:
            data = Product.objects.get(productId=code)
            data.searched += 1
            products = {}
            products["image"] = data.image1
            products["productName"] = data.productName
            products["selling"] = data.sellingPrice
            products["actual"] = data.actualPrice
            products["id"] = data.productId
            data.save()
            productMain.append(products)

        for shop in shops:
            count = 0
            username = shop.username
            shopName = shop.shopName.lower()
            shopDesc = shop.description.lower()
            shopCat = shop.categories.lower()
            shopId = User.objects.get(username=username).id
            for text in searchText:
                if (text in str(username)) or (text in shopName) or (text in shopDesc) or (text in shopCat):
                    count += 1
            if count > 0:
                shopDict[shopId] = count

        sortedId = sorted(shopDict, key=shopDict.get)  # [1, 3, 2]

        shopMain = []
        for code in sortedId:
            data = Shop.objects.get(username=code)
            data.searched += 1
            shop = {}
            shop["image"] = data.image1
            shop["shopName"] = data.shopName
            shop["owner"] = data.owner
            shop["categories"] = data.categories
            shop["id"] = data.username
            data.save()
            shopMain.append(shop)

    if len(shopMain) != 0 or len(productMain) != 0:
        isDisable = True

    context = {
        "products": productMain,
        "shops": shopMain,
        "disable": isDisable,
        "typeOf": typeOf,
    }

    return render(request, "productSearch.html", context)


def ajaxDeleteProduct(request):
    result = "false"
    productId = request.POST.get('productId', None)

    if request.user != "AnonymousUser":
        userProduct = Product.objects.filter(productId=productId)
        if len(userProduct):
            userProduct[0].delete()
            result = "true"

    data1 = {
        'result': result,
    }
    return JsonResponse(data1, safe=False)


def myOrders(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "wholeseller":
        return redirect("/login")

    userData = UserInfo.objects.get(username=request.user)
    orders = userData.buyedProducts.split(",")
    products = []

    if len(orders[0]) != 0:
        for order in orders[:-1]:
            data = {}
            order = order.split(":;:")
            productId = order[0]
            qty = order[1]
            productDetail = Product.objects.get(productId=productId)
            data["productId"] = productId
            data["productName"] = productDetail.productName
            data["image"] = productDetail.image1
            data["category"] = productDetail.category
            data["shopId"] = productDetail.username
            data["qty"] = qty
            userId = User.objects.get(username=data["shopId"]).id
            data["shopName"] = Shop.objects.get(username=userId).shopName
            products.append(data)

    context = {
        "data": products,
        "typeOf": typeOf,
    }

    return render(request, "myOrders.html", context)


def ordered(request):
    typeOf = typeOfUser(request.user)
    if request.user.is_anonymous or typeOf == "wholeseller":
        return redirect("/login")

    products = []
    bill = {}
    total = 0
    userInfo = UserInfo.objects.filter(username=request.user)
    if len(userInfo):
        userData = userInfo[0]
        cart = userData.cart.split(",")[:-1]
        for item in cart:
            data = {}
            itemSplit = item.split(":;:")
            product = itemSplit[0]
            qty = itemSplit[1]
            productDetail = Product.objects.get(productId=product)
            productName = productDetail.productName
            productBill = int(productDetail.sellingPrice) * int(qty)
            productDetail.stock -= int(qty)
            productDetail.buyed += int(qty)
            productDetail.save()
            shopDetail = Shop.objects.get(
                username=User.objects.get(username=product.split("-")[0]).id)
            shopDetail.productBuyed = str(
                request.user) + ":;:" + product + ":;:" + qty + ","
            shopDetail.totalSale += int(qty)
            shopDetail.totalStock -= int(qty)
            shopDetail.save()
            data["productName"] = productName
            data["qty"] = qty
            data["productBill"] = productBill
            products.append(data)
            total += productBill
        userData = UserInfo.objects.get(username=request.user)
        userData.buyed += int(qty)
        userData.buyedProducts = userData.cart
        userData.cart = ""
        userData.save()

        bill["date"] = date.today()
        bill["total"] = total + 180
        bill["orderId"] = str(request.user) + "-" + \
            str(random.randint(10000000, 99999999))

    context = {
        "products": products,
        "bill": bill,
        "typeOf": typeOf,
    }

    return render(request, "ordered.html", context)


def typeOfUser(user):
    userData = UserInfo.objects.get(username=user)
    return userData.typeOf
