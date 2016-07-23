from django.utils.translation import ugettext_lazy as _
from django_comments_xtd.forms import XtdCommentForm


class MyCommentForm(XtdCommentForm):
    def __init__(self, *args, **kwargs):
        if 'comment' in kwargs:
            followup_suffix = ('_%d' % kwargs['comment'].pk)
        else:
            followup_suffix = ''
        super(MyCommentForm, self).__init__(*args, **kwargs)
        for field_name, field_obj in self.fields.items():
            if field_name == 'followup':
                field_obj.widget.attrs['id'] = 'id_followup%s' % followup_suffix
            else:
                field_obj.widget.attrs.update({'class': 'form-control'})
                if field_name == 'comment':
                    field_obj.widget.attrs.pop('cols')
                    field_obj.widget.attrs.pop('rows')
                    field_obj.widget.attrs['placeholder'] = _('Your comment')
                    field_obj.widget.attrs['style'] = "font-size: 1.1em"
                if field_name == 'url':
                    field_obj.help_text = _('Optional')
        self.fields.move_to_end('comment', last=False)
