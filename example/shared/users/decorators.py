from django.conf import settings
from django.http import HttpResponseRedirect


def not_authenticated(func=None):
    """
    Decorator that redirect user to its account settings entry if it is
    already logged in.
    """

    def decorated(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        return func(request, *args, **kwargs)

    return decorated
