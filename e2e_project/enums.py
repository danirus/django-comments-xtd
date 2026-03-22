from django.utils.translation import gettext as _

from django_comments_xtd.models import BaseReactionEnum


# ----------------------------------------------------
class ReactionEnum(BaseReactionEnum):
    LIKE_IT = "+", _("Like")
    DISLIKE_IT = "-", _("Dislike")
    SMILE = "S", _("Smile")
    CONFUSED = "C", _("Confused")
    GREAT = "G", _("Great")
    HEART = "H", _("Heart")
    ROCKET = "R", _("Rocket")
    EYES = "E", _("Eyes")


ReactionEnum.set_icons(
    {
        ReactionEnum.LIKE_IT: "👍",
        ReactionEnum.DISLIKE_IT: "👎",
        ReactionEnum.SMILE: "😀",
        ReactionEnum.CONFUSED: "😕",
        ReactionEnum.GREAT: "🎉",
        ReactionEnum.ROCKET: "🚀",
        ReactionEnum.HEART: "❤️",
        ReactionEnum.EYES: "👀",
    }
)
