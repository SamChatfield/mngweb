from django import template

from ..utils import user_is_project_owner, user_is_project_contact
from ..forms import EmailLinkForm


register = template.Library()

@register.inclusion_tag('portal/tags/email_link_form.html', takes_context=True)
def email_link_form(context):
    return {
        'request': context['request'],
        'form': EmailLinkForm(),
    }

register.simple_tag(user_is_project_owner)
register.simple_tag(user_is_project_contact)
