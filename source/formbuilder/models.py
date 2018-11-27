from __future__ import unicode_literals
import datetime

from django.db import models
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, get_connection
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.six import text_type

from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import (FieldPanel, PageChooserPanel,
                                                MultiFieldPanel, InlinePanel)
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField


class FormField(AbstractFormField):
    page = ParentalKey('FormPage', related_name='form_fields')


class FormThankYouPage(Page):
    message = RichTextField(blank=True)
    parent_page_types = [
        'formbuilder.FormPage',
        'quote.QuoteRequestFormPage',
    ]

    # exclude from sitemap
    def get_sitemap_urls(self):
        return []

    content_panels = Page.content_panels + [
        FieldPanel('message', classname="full")
    ]


class FormPage(AbstractEmailForm):
    intro = RichTextField(blank=True)
    side_panel_title = models.CharField(max_length=255, blank=True)
    side_panel_content = RichTextField(blank=True)
    success_message = models.CharField(max_length=255)
    thank_you_page = models.ForeignKey(
        'formbuilder.FormThankYouPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    subpage_types = ['formbuilder.FormThankYouPage']


    # Override send_mail method to add 'reply-to' header, timestamp subject
    def send_mail(self, form):
        addresses = [x.strip() for x in self.to_address.split(',')]
        content = []
        reply_to = ([form.data['email']] if 'email' in form.data else None)

        # Add timestamp to subject, to avoid gmail-style conversation views
        time = str(datetime.datetime.now()).split('.')[0]
        subject = '{} [{}]'.format(self.subject, time)

        for field in form:
            value = field.value()
            if isinstance(value, list):
                value = ', '.join(value)
            content.append('{}: {}'.format(field.label, value))
        content = '\n'.join(content)
        connection = get_connection(username=settings.EMAIL_HOST_USER_INTERNAL,
                                    password=settings.EMAIL_HOST_PASSWORD_INTERNAL)
        email = EmailMessage(subject, content, self.from_address, addresses,
                             connection=connection, reply_to=reply_to)
        email.send(fail_silently=False)


    # Override serve method to enable ajax
    def serve(self, request):
        if request.method == 'POST':
            # honeypot
            if len(request.POST.get('url_h', '')):
                messages.success(request, self.success_message)
                return HttpResponseRedirect(self.url)

            form = self.get_form(request.POST)

            if form.is_valid():
                self.process_form_submission(form)
                messages.success(request, self.success_message)

                if request.is_ajax():
                    # Valid ajax post
                    data = {'messages': []}
                    for message in messages.get_messages(request):
                        data['messages'].append({
                            "level": message.level,
                            "level_tag": message.level_tag,
                            "message": message.message,
                        })
                    data['messages_html'] = render_to_string(
                        'includes/messages.html',
                        {'messages': messages.get_messages(request)})
                    return JsonResponse(data)
                else:
                    # Valid (non-ajax) post
                    if self.thank_you_page:
                        return HttpResponseRedirect(self.thank_you_page.url)
                    else:
                        return HttpResponseRedirect(self.url)

            elif request.is_ajax():
                # Invalid ajax post
                data = {'errors': form.errors}
                return JsonResponse(data, status=400)

        else:
            # GET request
            form = self.get_form()

        context = self.get_context(request)
        context['form'] = form
        return render(
            request,
            self.template,
            context
        )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro', classname="full"),
        MultiFieldPanel([
            FieldPanel('side_panel_title'),
            FieldPanel('side_panel_content', classname="full"),
        ], "Side Panel"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('success_message', classname="full"),
        PageChooserPanel('thank_you_page'),
        MultiFieldPanel([
            FieldPanel('to_address', classname="full"),
            FieldPanel('from_address', classname="full"),
            FieldPanel('subject', classname="full"),
        ], "Email")
    ]
