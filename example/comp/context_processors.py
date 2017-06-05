from django_comments_xtd.conf import settings as _settings

def settings(request):
    return {'settings': _settings}
