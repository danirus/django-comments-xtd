from django.db import models
from django.urls import reverse

# Every instance of Story has an associated test_spec to run.


class LoggedOutSpec(models.Model):
    """JavaScript test specs."""

    spec_path = models.CharField("spec_path", max_length=64)
    slug = models.SlugField("slug", unique=True, primary_key=True)

    class Meta:
        verbose_name_plural = "Logged out specs"

    def __str__(self):
        return f"{self.slug}"

    def get_absolute_url(self):
        return reverse(
            "logged-out-spec-detail",
            kwargs={
                "slug": self.slug,
            },
        )
