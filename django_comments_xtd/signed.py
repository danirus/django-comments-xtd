"""
Borrowed from Simon Willison's Django-OpenID project:
  * https://github.com/simonw/django-openid

Functions for creating and restoring url-safe signed pickled objects.

The format used looks like this:

>>> signed.dumps("hello")
'UydoZWxsbycKcDAKLg.AfZVu7tE6T1K1AecbLiLOGSqZ-A'

There are two components here, separatad by a '.'. The first component is a
URLsafe base64 encoded pickle of the object passed to dumps(). The second
component is a base64 encoded hmac/SHA1 hash of "$first_component.$secret"

Calling signed.loads(s) checks the signature BEFORE unpickling the object -
this protects against malformed pickle attacks. If the signature fails, a
ValueError subclass is raised (actually a BadSignature):

>>> signed.loads('UydoZWxsbycKcDAKLg.AfZVu7tE6T1K1AecbLiLOGSqZ-A')
'hello'
>>> signed.loads('UydoZWxsbycKcDAKLg.AfZVu7tE6T1K1AecbLiLOGSqZ-A-modified')
...
BadSignature: Signature failed: AfZVu7tE6T1K1AecbLiLOGSqZ-A-modified

You can optionally compress the pickle prior to base64 encoding it to save
space, using the compress=True argument. This checks if compression actually
helps and only applies compression if the result is a shorter string:

>>> signed.dumps(range(1, 10), compress=True)
'.eJzTyCkw4PI05Er0NAJiYyA2AWJTIDYDYnMgtgBiS65EPQDQyQme.EQpzZCCMd3mIa4RXDGnAuMCCAx0'

The fact that the string is compressed is signalled by the prefixed '.' at the
start of the base64 pickle.

There are 65 url-safe characters: the 64 used by url-safe base64 and the '.'.
These functions make use of all of them.
"""
from __future__ import unicode_literals

import base64
import hmac
import pickle
import hashlib

from django.utils import six
from django_comments_xtd.conf import settings


def dumps(obj, key=None, compress=False, extra_key=b''):
    """
    Returns URL-safe, sha1 signed base64 compressed pickle. If key is
    None, settings.SECRET_KEY is used instead.

    If compress is True (not the default) checks if compressing using zlib can
    save some space. Prepends a '.' to signify compression. This is included
    in the signature, to protect against zip bombs.

    extra_key can be used to further salt the hash, in case you're worried
    that the NSA might try to brute-force your SHA-1 protected secret.
    """
    pickled = pickle.dumps(obj)
    is_compressed = False  # Flag for if it's been compressed or not
    if compress:
        import zlib  # Avoid zlib dependency unless compress is being used
        compressed = zlib.compress(pickled)
        if len(compressed) < (len(pickled) - 1):
            pickled = compressed
            is_compressed = True
    base64d = encode(pickled).strip(b'=')
    if is_compressed:
        base64d = b'.' + base64d
    return sign(base64d,
                (key or settings.SECRET_KEY.encode('ascii')) + extra_key)


def loads(s, key=None, extra_key=b''):
    "Reverse of dumps(), raises ValueError if signature fails"
    if isinstance(s, six.text_type):
        s = s.encode('utf8')  # base64 works on bytestrings
    try:
        base64d = unsign(s,
                         (key or settings.SECRET_KEY.encode('ascii')) +
                         extra_key)
    except ValueError:
        raise
    decompress = False
    if base64d.startswith(b'.'):
        # It's compressed; uncompress it first
        base64d = base64d[1:]
        decompress = True
    pickled = decode(base64d)
    if decompress:
        import zlib
        pickled = zlib.decompress(pickled)
    return pickle.loads(pickled)


def encode(s):
    return base64.urlsafe_b64encode(s).strip(b'=')


def decode(s):
    return base64.urlsafe_b64decode(s + b'=' * (len(s) % 4))


class BadSignature(ValueError):
    # Extends ValueError, which makes it more convenient to catch and has
    # basically the correct semantics.
    pass


def sign(value, key=None):
    if isinstance(value, six.text_type):
        raise TypeError('sign() needs bytestring: %s' % repr(value))
    if key is None:
        key = settings.SECRET_KEY.encode('ascii')
    return value + b'.' + base64_hmac(value, key)


def unsign(signed_value, key=None):
    if isinstance(signed_value, six.text_type):
        raise TypeError('unsign() needs bytestring')
    if key is None:
        key = settings.SECRET_KEY.encode('ascii')
    if signed_value.find(b'.') == -1:
        raise BadSignature('Missing sig (no . found in value)')
    value, sig = signed_value.rsplit(b'.', 1)
    if base64_hmac(value, key) == sig:
        return value
    else:
        raise BadSignature('Signature failed: %s' % sig)


def base64_hmac(value, key):
    return encode(hmac.new(key, value, hashlib.sha1).digest())
