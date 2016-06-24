from __future__ import unicode_literals

from django.db import models
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel,\
    PageChooserPanel

from .forms import QuoteRequestForm


class QuoteRequestFormPage(Page):
    """
    A Quote Request Form Page that sends email and creates a
    FormSubmission record.
    """

    intro = RichTextField(blank=True)
    side_panel_title = models.CharField(max_length=255)
    side_panel_content = RichTextField(blank=True)
    success_message = models.CharField(max_length=255)
    thank_you_page = models.ForeignKey(
        'formbuilder.FormThankYouPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    to_address = models.EmailField(
        max_length=255,
        help_text="Form submissions will be emailed to this address")
    from_address = models.EmailField(
        max_length=255,
        help_text="Form submissions will show as having come from this"
        " address")
    subject = models.CharField(max_length=255, blank=True)

    subpage_types = ['formbuilder.FormThankYouPage']

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full'),
        MultiFieldPanel([
            FieldPanel('side_panel_title'),
            FieldPanel('side_panel_content', classname='full'),
        ], "Side Panel"),
        MultiFieldPanel([
            FieldPanel('to_address'),
            FieldPanel('from_address'),
            FieldPanel('subject', classname="full"),
        ], "Email"),
        PageChooserPanel('thank_you_page'),
    ]

    def process_form_submission(self, form):
        if self.to_address:
            content = '\n'.join(
                [(o.label if o.label else f) + ': ' + str(form.cleaned_data[f])
                    for f, o in form.fields.items()]
            )
            reply_to = ([form.data['email']] if 'email' in form.data else None)
            email = EmailMessage(self.subject, content, self.from_address,
                                 [self.to_address], reply_to=reply_to)
            email.send(fail_silently=False)

    def serve(self, request):
        if request.method == 'POST':
            # honeypot
            if len(request.POST.get('url_h', '')):
                messages.success(request, self.success_message)
                return HttpResponseRedirect(self.url)

            form = QuoteRequestForm(request.POST)

            if form.is_valid():
                self.process_form_submission(form)
                if self.thank_you_page:
                    return HttpResponseRedirect(self.thank_you_page.url)
                else:
                    messages.success(request, self.success_message)
                    return HttpResponseRedirect(self.url)
        else:
            form = QuoteRequestForm()

        return render(request, 'quote/quote_request_form.html', {
            'page': self,
            'form': form,
        })
