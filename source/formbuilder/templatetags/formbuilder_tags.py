from django import template

from ..models import FormPage


register = template.Library()


# Contact form

@register.inclusion_tag('formbuilder/tags/contact_form.html', takes_context=True)
def contact_form(context):
    page = FormPage.objects.get(slug='contact')
    return {
        'request': context['request'],
        'page': page,
        'form': page.get_form(),
    }
