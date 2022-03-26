"""
Tests borrowed from Simon Willison's Django-OpenID project:
  * https://github.com/simonw/django-openid
"""
import pytest

from django.conf import settings

from django_comments_xtd import signed


def test_sign_unsign_no_unicode():
    "sign/unsign functions should not accept unicode strings"
    with pytest.raises(TypeError):
        signed.sign("\u2021")
    with pytest.raises(TypeError):
        signed.unsign("\u2021")


def test_sign_uses_correct_key():
    "If a key is provided, sign should use it; otherwise, use SECRET_KEY"
    s = b"This is a string"

    assert signed.sign(s) == (
        s + b"." + signed.base64_hmac(s, settings.SECRET_KEY.encode("ascii"))
    )
    assert signed.sign(s, b"sekrit") == (
        s + b"." + signed.base64_hmac(s, b"sekrit")
    )


def test_sign_is_reversible():
    examples = (
        b"q;wjmbk;wkmb",
        b"3098247529087",
        b"3098247:529:087:",
        b"jkw osanteuh ,rcuh nthu aou oauh ,ud du",
        "\u2019".encode("utf8"),
    )
    for example in examples:
        assert example != signed.sign(example)
        assert example == signed.unsign(signed.sign(example))


def test_unsign_detects_tampering():
    value = b"Another string"
    signed_value = signed.sign(value)
    transforms = (
        lambda s: s.upper(),
        lambda s: s + b"a",
        lambda s: b"a" + s[1:],
        lambda s: s.replace(b".", b""),
    )
    assert value == signed.unsign(signed_value)
    for transform in transforms:
        with pytest.raises(signed.BadSignature):
            signed.unsign(transform(signed_value))


def test_encode_decode():
    objects = (
        (b"a", b"tuple"),
        b"a string",
        "a unicode string \u2019",
        {"a": "dictionary"},
    )
    for o in objects:
        assert o != signed.dumps(o)
        assert o == signed.loads(signed.dumps(o))


def test_decode_detects_tampering():
    transforms = (
        lambda s: s.upper(),
        lambda s: s + b"a",
        lambda s: b"a" + s[1:],
        lambda s: s.replace(b".", b""),
    )
    value = {"foo": "bar", "baz": 1}
    encoded = signed.dumps(value)
    assert value == signed.loads(encoded)
    for transform in transforms:
        with pytest.raises(signed.BadSignature):
            signed.loads(transform(encoded))
