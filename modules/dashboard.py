import numpy as np
import matplotlib.pyplot as plt
from ecommerce.settings import MEDIA_ROOT
from Main.models import UserInfo,Product,Shop

def dashboard(value1, value2, value3):
    total  = 120
    totalVisited = 120 - 90
    totalSale = 38
    y = np.array([totalSale,totalVisited])
    mylabels = ["Purchased (38)", "Not Purchased"]
    myexplode = [0.2, 0]
    mycolors = ["g", "r"]
    print(UserInfo.objects.get(username = 1))
    plt.pie(y, labels = mylabels, explode = myexplode,  autopct='%.2f', colors = mycolors, shadow = True)
    plt.title(label="Your Sales w.r.t. Visits", loc="center", fontstyle='oblique') 
    plt.xlabel("Shop Visited : " + str(total))
    plt.savefig((MEDIA_ROOT + r"\dashboard\testing.png"))
    return "hello"
