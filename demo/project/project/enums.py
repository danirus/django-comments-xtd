from django.utils.translation import ugettext as _

from django_comments_xtd.models import BaseReactionEnum


class ReactionEnum(BaseReactionEnum):
    LIKE_IT =    "+", _("Like")
    DISLIKE_IT = "-", _("Dislike")
    SMILE =      "S", _("Smile")
    CONFUSED =   "C", _("Confused")
    GREAT =      "G", _("Great")
    HEART =      "H", _("Heart")
    ROCKET =     "R", _("Rocket")
    EYES =       "E", _("Eyes")


ReactionEnum.set_icons({
    ReactionEnum.LIKE_IT:    "#128077",
    ReactionEnum.DISLIKE_IT: "#128078",
    ReactionEnum.SMILE:      "#128512",
    ReactionEnum.CONFUSED:   "#128533",
    ReactionEnum.GREAT:      "#127881",
    ReactionEnum.HEART:      "#10084",
    ReactionEnum.ROCKET:     "#128640",
    ReactionEnum.EYES:       "#128064"
})