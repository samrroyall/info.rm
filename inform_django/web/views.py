from django.shortcuts import render, redirect
import math

# Create your views here.
def index(response):
    return redirect("/dashboards")

def dashboards(response):
    data = [
        [1,2,3,4,5,6,7,8,9,10],
        [11,12,13,14,15],
    ]
    context = {
        "data": data,
    }
    return render(response, "dashboards.html", context)

def builder(request):
    context = {
    }
    return render(request, "builder.html", context)


