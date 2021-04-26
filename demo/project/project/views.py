from django.shortcuts import render
# from django.template import RequestContext


def home(request):
    # context = RequestContext(request)
    return render(request, "homepage.html")