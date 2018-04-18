from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, get_connection
from django.http import HttpResponseRedirect
from django.shortcuts import render

from wagtail.wagtailadmin.edit_handlers import (FieldPanel, MultiFieldPanel,
                                                PageChooserPanel)
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from portal.services import limsfm_create_quote
from .forms import QuoteRequestForm


class QuoteRequestFormPage(RoutablePageMixin, Page):
    """
    A Quote Request Form Page that sends an email and calls LIMSfm API to create
    a draft quote.
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
        try:
            quote_ref = limsfm_create_quote(form.cleaned_data)
        except Exception:
            quote_ref = ''

        # send email
        if self.to_address:
            addresses = [x.strip() for x in self.to_address.split(',')]
            content = []
            content.append('Quote Ref: {}'.format(quote_ref))

            for field in form:
                value = field.value()
                if isinstance(value, list):
                    value = ', '.join(value)
                content.append('{}: {}'.format(field.label, value))
            content = '\n'.join(content)

            reply_to = ([form.data['email']] if 'email' in form.data else None)
            subject = '%s [%s %s]' % (self.subject, quote_ref, form.data['name_last'])
            connection = get_connection(username=settings.EMAIL_HOST_USER_INTERNAL,
                                        password=settings.EMAIL_HOST_PASSWORD_INTERNAL)
            email = EmailMessage(subject, content, self.from_address, [self.to_address],
                                 connection=connection, reply_to=reply_to)
            email.send(fail_silently=False)


    # def serve(self, request):
    #     if request.method == 'POST':
    #         # honeypot
    #         if len(request.POST.get('url_h', '')):
    #             messages.success(request, self.success_message)
    #             return HttpResponseRedirect(self.url)

    #         form = QuoteRequestForm(request.POST)

    #         if form.is_valid():
    #             self.process_form_submission(form)
    #             if self.thank_you_page:
    #                 return HttpResponseRedirect(self.thank_you_page.url)
    #             else:
    #                 messages.success(request, self.success_message)
    #                 return HttpResponseRedirect(self.url)
    #     else:
    #         form = QuoteRequestForm()

    #     return render(request, 'quote/quote_request_form.html', {
    #         'page': self,
    #         'form': form,
    #     })


    @route(r'^$')
    @route(r'^(?P<service_string>[\w\-]+)/$')
    def service_serve(self, request, service_string = None):
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
            'service_string': service_string
        })