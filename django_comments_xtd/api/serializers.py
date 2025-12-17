from typing import ClassVar

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.utils import formats, timezone
from django.utils.html import escape
from django.utils.translation import activate, get_language
from django.utils.translation import gettext as _
from django_comments import get_form
from django_comments.forms import CommentSecurityForm
from django_comments.models import CommentFlag
from django_comments.signals import comment_was_posted, comment_will_be_posted
from rest_framework import exceptions, serializers

from django_comments_xtd import get_model, get_reaction_enum, signed
from django_comments_xtd.conf import settings
from django_comments_xtd.models import (
    CommentReaction,
    CommentReactionAuthor,
    CommentVote,
    TmpXtdComment,
    XtdComment,
)
from django_comments_xtd.signals import (
    confirmation_received,
    should_request_be_authorized,
)
from django_comments_xtd.utils import (
    get_app_model_config,
    get_max_thread_level,
)
from django_comments_xtd.views import (
    create_comment,
    get_comment_if_exists,
    notify_comment_followers,
    send_email_confirmation_request,
)

COMMENT_MAX_LENGTH = getattr(settings, "COMMENT_MAX_LENGTH", 3000)


class WriteCommentSerializer(serializers.Serializer):
    content_type = serializers.CharField()
    object_pk = serializers.CharField()
    timestamp = serializers.CharField(required=False)
    security_hash = serializers.CharField(required=False)
    honeypot = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(allow_blank=True)
    email = serializers.EmailField(allow_blank=True)
    url = serializers.URLField(required=False)
    comment = serializers.CharField(max_length=COMMENT_MAX_LENGTH)
    followup = serializers.BooleanField(default=False)
    reply_to = serializers.IntegerField(default=0)

    def __init__(self, *args, **kwargs):
        self.request = kwargs["context"]["request"]
        super().__init__(*args, **kwargs)

    def validate_name(self, value):
        if value.strip():
            return value.strip()
        if self.request.user.is_authenticated:
            name = None
            if hasattr(self.request.user, "get_full_name"):
                name = self.request.user.get_full_name()
            elif hasattr(self.request.user, "get_username"):
                name = self.request.user.get_username()
            if name:
                return name
        raise serializers.ValidationError("This field is required")

    def validate_email(self, value):
        if value.strip():
            return value.strip()
        if self.request.user.is_authenticated:
            UserModel = apps.get_model(settings.AUTH_USER_MODEL)  # ruff: N806
            if hasattr(UserModel, "get_email_field_name"):
                email_field = UserModel.get_email_field_name()
                email = getattr(self.request.user, email_field, None)
                if email:
                    return email
        raise serializers.ValidationError("This field is required")

    def validate_reply_to(self, value):
        if value != 0:
            try:
                parent = get_model().objects.get(pk=value)
            except get_model().DoesNotExist as exc:
                raise serializers.ValidationError(
                    "reply_to comment does not exist"
                ) from exc
            else:
                max = get_max_thread_level(parent.content_type)
                if parent.level == max:
                    raise serializers.ValidationError(
                        "Max thread level reached"
                    )
        return value

    def validate(self, data):
        content_type = data.get("content_type")
        object_pk = data.get("object_pk")
        try:
            model = apps.get_model(*content_type.split(".", 1))
            target = model._default_manager.get(pk=object_pk)
            ctype = ContentType.objects.get_for_model(model)
            whocan = get_app_model_config(content_type=ctype)["who_can_post"]
        except (AttributeError, TypeError, LookupError) as exc:
            raise serializers.ValidationError(
                f"Invalid content_type value: {escape(content_type)!r}"
            ) from exc
        except model.DoesNotExist as exc:
            raise serializers.ValidationError(
                "No object matching content-type "
                f"{escape(content_type)!r} and object PK "
                f"{escape(object_pk)!r}."
            ) from exc
        except (ValueError, serializers.ValidationError) as exc:
            raise serializers.ValidationError(
                f"Attempting to get content-type {escape(content_type)!r} "
                f"and object PK {escape(object_pk)!r} raised {exc}"
            ) from exc
        else:
            if whocan == "users" and not self.request.user.is_authenticated:
                raise serializers.ValidationError("User not authenticated")

        # Signal that the request allows to be authorized.
        responses = should_request_be_authorized.send(
            sender=target.__class__, comment=target, request=self.request
        )

        for __, response in responses:
            if response is True:
                # A positive response indicates that the POST request
                # must be trusted. So inject the CommentSecurityForm values
                # to pass the form validation step.
                secform = CommentSecurityForm(target)
                data.update(
                    {
                        "honeypot": "",
                        "timestamp": secform["timestamp"].value(),
                        "security_hash": secform["security_hash"].value(),
                    }
                )
                break

        self.form = get_form()(target, data=data)
        if not self.form.is_valid() and self.form.security_errors():
            # Check only security information as the rest
            # of the fields have already been validated.
            raise exceptions.PermissionDenied()
        return data

    def save(self):
        # resp object is a dictionary. The code key indicates the possible
        # four states the comment can be in:
        #  * Comment created (http 201),
        #  * Confirmation sent by mail (http 204),
        #  * Comment in moderation (http 202),
        #  * Comment rejected (http 403),
        #  * Comment have bad data (http 400).
        site = get_current_site(self.request)
        resp = {
            "code": -1,
            "comment": self.form.get_comment_object(site_id=site.id),
        }
        resp["comment"].ip_address = self.request.META.get("REMOTE_ADDR", None)

        if self.request.user.is_authenticated:
            resp["comment"].user = self.request.user

        # Signal that the comment is about to be saved
        responses = comment_will_be_posted.send(
            sender=TmpXtdComment, comment=resp["comment"], request=self.request
        )
        for __, response in responses:
            if response is False:
                resp["code"] = 403  # Rejected.
                return resp

        # Replicate logic from on_comment_was_posted.
        if (
            not settings.COMMENTS_XTD_CONFIRM_EMAIL
            or self.request.user.is_authenticated
        ):
            if get_comment_if_exists(resp["comment"]) is None:
                new_comment = create_comment(resp["comment"])
                resp["comment"].xtd_comment = new_comment
                confirmation_received.send(
                    sender=TmpXtdComment,
                    comment=resp["comment"],
                    request=self.request,
                )
                comment_was_posted.send(
                    sender=new_comment.__class__,
                    comment=new_comment,
                    request=self.request,
                )
                if resp["comment"].is_public:
                    resp["code"] = 201
                    notify_comment_followers(new_comment)
                else:
                    resp["code"] = 202
        else:
            key = signed.dumps(
                resp["comment"],
                compress=True,
                extra_key=settings.COMMENTS_XTD_SALT,
            )
            send_email_confirmation_request(resp["comment"], key, site)
            resp["code"] = 204  # Confirmation sent by mail.

        return resp


class FlagSerializer(serializers.ModelSerializer):
    flag_choices: ClassVar = {"report": CommentFlag.SUGGEST_REMOVAL}

    class Meta:
        model = CommentFlag
        fields = (
            "comment",
            "flag",
        )

    def validate(self, data):
        # Validate flag.
        if data["flag"] not in self.flag_choices:
            raise serializers.ValidationError("Invalid flag.")
        data["flag"] = self.flag_choices[data["flag"]]
        return data


class ReadReactionsField(serializers.RelatedField):
    def to_representation(self, value):
        reaction_item = get_reaction_enum()(value.reaction)
        max_users_listed = getattr(
            settings, "COMMENTS_INK_MAX_USERS_IN_TOOLTIP", 10
        )
        return {
            "reaction": value.reaction,
            "label": reaction_item.label,
            "icon": reaction_item.icon,
            "counter": value.counter,
            "authors": [
                {
                    "id": author.id,
                    "author": settings.COMMENTS_XTD_FN_USER_REPR(author),
                }
                for author in value.authors.all()[:max_users_listed]
            ],
        }


class ReadCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(max_length=50, read_only=True)
    user_url = serializers.CharField(read_only=True)
    submit_date = serializers.SerializerMethodField()
    parent_id = serializers.IntegerField(default=0, read_only=True)
    level = serializers.IntegerField(read_only=True)
    is_removed = serializers.BooleanField(read_only=True)
    comment = serializers.SerializerMethodField()
    allow_reply = serializers.SerializerMethodField()
    permalink = serializers.SerializerMethodField()
    flags = serializers.SerializerMethodField()
    reactions = ReadReactionsField(many=True, read_only=True)

    class Meta:
        model = XtdComment
        fields = (
            "id",
            "user_name",
            "user_url",
            "permalink",
            "comment",
            "submit_date",
            "parent_id",
            "level",
            "is_removed",
            "allow_reply",
            "flags",
            "reactions",
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs["context"]["request"]
        super().__init__(*args, **kwargs)

    def get_submit_date(self, obj):
        activate(get_language())
        if settings.USE_TZ:
            submit_date = timezone.localtime(obj.submit_date)
        else:
            submit_date = obj.submit_date
        return formats.date_format(
            submit_date, "DATETIME_FORMAT", use_l10n=True
        )

    def get_comment(self, obj):
        if obj.is_removed:
            return _("This comment has been removed.")
        else:
            return obj.comment

    def get_allow_reply(self, obj):
        return obj.allow_thread()

    def get_permalink(self, obj):
        return obj.get_absolute_url()

    def get_flags(self, obj):
        qs = obj.flags.filter(flag=CommentFlag.SUGGEST_REMOVAL)
        return [
            {
                "flag": "removal",
                "user": settings.COMMENTS_XTD_FN_USER_REPR(flag.user),
                "id": flag.user.id,
            }
            for flag in qs
        ]


class WriteCommentReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReaction
        fields = (
            "reaction",
            "comment",
        )


class ReadCommentReactionAuthorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = CommentReactionAuthor
        fields = (
            "id",
            "author",
        )

    def get_author(self, obj):
        return settings.COMMENTS_XTD_FN_USER_REPR(obj)


class WriteCommentVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentVote
        fields = (
            "vote",
            "comment",
        )
