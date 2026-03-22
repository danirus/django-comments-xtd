from django.apps import AppConfig


class DjangoCypressConfig(AppConfig):
    """Configuration class for the django_cypress app.

    It provides settings like the name or the label of
    the Django App.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cypress"
    label = "django_cypress"
