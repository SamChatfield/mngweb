from __future__ import unicode_literals

import json

from django.db import models
from django.core.mail import EmailMessage
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.utils.six import text_type

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailforms.models import FormSubmission

from .forms import QuoteRequestForm


class QuoteRequestFormPage(Page):
    """
    A Quote Request Form Page that sends email and creates a
    FormSubmission record.
    """

    intro = RichTextField(blank=True)
    side_panel_title = models.CharField(max_length=255)
    side_panel_content = RichTextField(blank=True)

    to_address = models.EmailField(
        max_length=255, blank=True,
        help_text="Form submissions will be emailed to this address"
    )
    subject = models.CharField(max_length=255, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full'),
        MultiFieldPanel([
            FieldPanel('side_panel_title'),
            FieldPanel('side_panel_content', classname='full'),
        ], "Side Panel"),
        MultiFieldPanel([
            FieldPanel('to_address'),
            FieldPanel('subject', classname="full"),
        ], "Email")
    ]

    def process_form_submission(self, form):
        FormSubmission.objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page=self,
        )
        if self.to_address:
            content = '\n'.join([x[1].label + ': ' +
                                text_type(form.data.get(x[0]))
                                for x in form.fields.items()])
            reply_to = ([form.data['email']] if 'email' in form.data else None)
            email = EmailMessage(self.subject, content, self.from_address,
                                 [self.to_address], reply_to=reply_to)
            email.send(fail_silently=False)

    def serve(self, request):
        if request.method == 'POST':
            form = QuoteRequestForm(request.POST)
            if form.is_valid():
                self.process_form_submission()
                return render(request, 'quote/quote_request_form.html', {
                    'page': self,
                    'form': form,
                })
        else:
            form = QuoteRequestForm()

        return render(request, 'quote/quote_request_form.html', {
            'page': self,
            'form': form,
        })
