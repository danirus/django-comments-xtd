from django.utils.translation import ugettext as _

from django_comments_xtd.models import BaseReactionEnum


class CompReactionEnum(BaseReactionEnum):
    LIKE_IT =    "+", "+1"
    DISLIKE_IT = "-", "-1"
    SMILE =      "S", _("Smile")
    CONFUSED =   "C", _("Confused")
    GREAT =      "G", _("Great")
    HEART =      "H", _("Heart")
    ROCKET =     "R", _("Rocket")
    EYES =       "E", _("Eyes")


CompReactionEnum.set_icons({
    CompReactionEnum.LIKE_IT:    "#128077",
    CompReactionEnum.DISLIKE_IT: "#128078",
    CompReactionEnum.SMILE:      "#128512",
    CompReactionEnum.CONFUSED:   "#128533",
    CompReactionEnum.GREAT:      "#127881",
    CompReactionEnum.HEART:      "#10084",
    CompReactionEnum.ROCKET:     "#128640",
    CompReactionEnum.EYES:       "#128064"
})