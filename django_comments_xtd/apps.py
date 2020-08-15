from django.apps import AppConfig
from django.db.models.signals import pre_save


class CommentsXtdConfig(AppConfig):
    name = 'django_comments_xtd'
    verbose_name = 'Comments Xtd'

    def ready(self):
        from django_comments_xtd import get_model
        from django_comments_xtd.models import publish_or_unpublish_on_pre_save

        model_app_label = get_model()._meta.label
        pre_save.connect(publish_or_unpublish_on_pre_save,
                         sender=model_app_label)
