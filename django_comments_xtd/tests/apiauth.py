from django.contrib.auth.models import AnonymousUser

from rest_framework import HTTP_HEADER_ENCODING, authentication, exceptions


class APIRequestAuthentication(authentication.BaseAuthentication):
  def authenticate(self, request):
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, str):
      auth = auth.encode(HTTP_HEADER_ENCODING)

    pieces = auth.split()
    if not pieces or pieces[0].lower() != b'token':
      return None

    if len(pieces) == 1:
      msg = _("Invalid token header. No credentials provided.")
      raise exceptions.AuthenticationFailed(msg)
    elif len(pieces) > 2:
      msg = _("Invalid token header."
          "Token string should not contain spaces.")
      raise exceptions.AuthenticationFailed(msg)

    try:
      auth = pieces[1].decode()
    except UnicodeError:
      msg = _("Invalid token header. "
          "Token string should not contain invalid characters.")

    return (AnonymousUser(), auth)