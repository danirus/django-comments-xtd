from django.apps import AppConfig
from django.db.models.signals import pre_save


class CommentsXtdConfig(AppConfig):
    name = 'django_comments_xtd'
    verbose_name = 'Comments Xtd'

    def ready(self):
        from django_comments_xtd import get_model
        from django_comments_xtd.conf import settings
        from django_comments_xtd.models import publish_or_withhold_on_pre_save

        if (
            getattr(settings, 'COMMENTS_HIDE_REMOVED', True) or
            getattr(settings, 'COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED', True)
        ):
            model_app_label = get_model()._meta.label
            pre_save.connect(publish_or_withhold_on_pre_save,
                             sender=model_app_label)
