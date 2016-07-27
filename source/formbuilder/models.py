from __future__ import unicode_literals

from django.db import models
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.six import text_type
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, \
    MultiFieldPanel, InlinePanel
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField
from modelcluster.fields import ParentalKey


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

    # Override process_form_submission method to add 'reply-to' header
    def process_form_submission(self, form):
        super(AbstractEmailForm, self).process_form_submission(form)

        if self.to_address:
            content = '\n'.join([x[1].label + ': ' +
                                text_type(form.data.get(x[0]))
                                for x in form.fields.items()])
            reply_to = ([form.data['email']] if 'email' in form.data else None)
            email = EmailMessage(self.subject, content, self.from_address,
                                 [self.to_address], reply_to=reply_to)
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
