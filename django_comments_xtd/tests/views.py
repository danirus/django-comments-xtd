from django.http import HttpResponse


def dummy_view(request, *args, **kwargs):
    return HttpResponse("Got it")
