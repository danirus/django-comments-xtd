import base64
import hashlib
import hmac
import os


def pwd_hexdigest(user):
    return hmac.new(
        os.environ.get('SECRET_KEY').encode('utf-8'),  # key
        user.password.encode('utf-8'),        # msg
        hashlib.sha256                        # digest method
    ).hexdigest()


def remember_me(response, user):
    email_utf_8 = user.email.encode('utf-8')
    cookie_content = base64.b64encode(email_utf_8).decode('utf-8')
    response.set_cookie("edids", cookie_content)
    response.set_cookie("cdids", pwd_hexdigest(user))


def forget_me(response):
    response.delete_cookie("edids")
    response.delete_cookie("cdids")
