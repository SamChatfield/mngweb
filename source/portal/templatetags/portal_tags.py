from django import template

from ..forms import EmailLinkForm


register = template.Library()


# Email Link form

@register.inclusion_tag('portal/tags/email_link_form.html', takes_context=True)
def email_link_form(context):
    return {
        'request': context['request'],
        'form': EmailLinkForm(),
    }
