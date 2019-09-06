import requests

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test

from .forms import (QuoteForm, ConfirmOrderForm)
from .models import (UniqueLink)

from portal.services import limsfm_request

from xero import Xero
from xero.auth import PrivateCredentials

from datetime import date, timedelta

def get_lims_quote(quote_code):
    response = limsfm_request('layout/quote_display_api', 'get', {
      'RFMmax' : 0,
      'RFMsF1' : 'reference',
      'RFMsV1' : '="{}"'.format(quote_code)
    })
    quote = response.json()['data']
    return quote

def get_lims_quoteline(quote):
    response = limsfm_request('layout/QuoteLine: Table', 'get', {
      'RFMmax' : 0,
      'RFMsF1' : 'quote_id',
      'RFMsV1' : '=' + str(quote['quote_id']),
    })
    return response.json()['data']

def get_lims_quotecontact(quote):
    response = limsfm_request('layout/quote_display_api', 'get', {
      'RFMmax' : 0,
      'RFMsF1' : 'quote_id',
      'RFMsV1' : '=' + str(quote['quote_id']),
    })
    return response.json()['data']

@user_passes_test(lambda u: u.is_superuser)
def create_order_link(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            qc = form.cleaned_data['quote_code']
            lq = get_lims_quote(qc)
            if not lq:
                return HttpResponse('Quote code does not exist!')

            ul = UniqueLink(quote_code=form.cleaned_data['quote_code'])
            ul.save()

            url = "https://microbesng.uk/order/%s" % (ul.unique_link,)
            return render(request, 'order/create_order_link.html', {'form' : QuoteForm(), 'link' : url})
        else:
            return render(request, 'order/create_order_link.html', {'form' : form})
    else:
        form = QuoteForm()
        return render(request, 'order/create_order_link.html', {'form' : form})

def xero_post_contact(cleaned_data, contact_number):
    credentials = PrivateCredentials(settings.XERO_CREDENTIALS, settings.XERO_PRIVATE_KEY)
    xero = Xero(credentials)

    lookup_contact = xero.contacts.filter(ContactNumber=contact_number)
    if lookup_contact:
        return lookup_contact[0]['ContactID']

    name = "%s (%s %s)" % (cleaned_data['organisation'], cleaned_data['name_first'], cleaned_data['name_last'])

    contact = {
        'Addresses': [ { 'AddressType': 'POBOX',
                         'City': cleaned_data['city'],
                         'Country': cleaned_data['country'],
                         'PostalCode': cleaned_data['postcode'],
                         'Region': cleaned_data['region'],
                         'AddressLine1' : cleaned_data['street_line_one'],
                         'AddressLine2' : cleaned_data['street_line_two'],
                         'AddressLine3' : cleaned_data['street_line_three'],
                       } ],
        'EmailAddress':  cleaned_data['email'],
        'Name':          name,
        'ContactNumber': contact_number
    }
    results = xero.contacts.put(contact)
    contact = results[0]
    return contact['ContactID']

european_country = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK',
                    'EE', 'FI', 'FR', 'DE', 'EL', 'HU', 'IE',
                    'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL',
                    'RO', 'SK', 'SI', 'ES', 'SE']

def xero_post_invoice(contact_id, unique_reference_id, quote, lines):
    credentials = PrivateCredentials(settings.XERO_CREDENTIALS, settings.XERO_PRIVATE_KEY)
    xero = Xero(credentials)

    today = date.today()
    due = date.today() + timedelta(days=30)

    if quote['vat_rate_percent'] == '0':
        if quote['Address::country_iso2'] in european_country:
            tax_type = 'ECZROUTPUTSERVICES'
        else:
            tax_type = 'ZERORATEDOUTPUT' 
    else:
        tax_type = 'OUTPUT2'

    invoice = {
        'Contact': {
             'ContactID': contact_id,
        },
        'Date': today,
        'DateString': today,
        'DueDate': due,
        'DueDateString': due,
        'IsDiscounted': False,
        'LineAmountTypes': 'Exclusive',
        'LineItems': [],
        'Reference': unique_reference_id,
        'Status': 'AUTHORISED',
        'Type': 'ACCREC',
    }

    for line in lines:
         description = "%s (quote: %s)" % (line['description'], quote['reference'])
         invoice['LineItems'].append({
             "Description" : description,
             "Quantity" : line['quantity'],
             "UnitAmount" : line['price'],
             "TaxType" : 'OUTPUT2',
             "AccountCode" : "REV-STD", ## TODO: lookup for account codes
             "TaxType" : tax_type
             #TODO ItemCode
         })

    results = xero.invoices.put(invoice)
    invoice = results[0]
    return invoice['InvoiceID']

def xero_get_payment_gateway(invoice_uuid):
    credentials = PrivateCredentials(settings.XERO_CREDENTIALS, settings.XERO_PRIVATE_KEY)
    xero = Xero(credentials)

    onlineinvoice_url = "%s/OnlineInvoice" % (invoice_uuid,)
    invoice = xero.invoices.get(onlineinvoice_url)

    href = "%s?utm_source=emailpaynowbutton#paynow" % (invoice['OnlineInvoices'][0]['OnlineInvoiceUrl'],)
    return href

def confirm_order(request, uuid):
    ul = get_object_or_404(UniqueLink, pk=uuid)

    if ul.xero_invoice_id:
         url = xero_get_payment_gateway(ul.xero_invoice_id)
         return render(request, 'order/order_already_processed.html', {'link' : url})

    lq = get_lims_quote(ul.quote_code)
    if not lq:
        raise HttpResponse('Sorry this quote was not found!')
    if len(lq) > 1:
        raise HttpResponse('Non unique quote!')
    quote = lq[0]

    lql = get_lims_quoteline(quote)

    if request.method == 'GET':
        form = ConfirmOrderForm()
        conversion = {
            'name_first' : 'Contact::name_first',
            'name_last'  : 'Contact::name_last',
            'organisation' : 'Organisation::name',
            'email' : 'Contact::email_address',
            'department' : 'Contact::department',
            'street_line_one' : 'Address::street_line_1',
            'street_line_two' : 'Address::street_line_3',
            'street_line_three' : 'Address::street_line_3',
            'city' : 'Address::city',
            'postcode' : 'Address::postcode',
            'country' : 'Address::country_iso2'
        }
        form.populate_form(conversion, quote)

        return render(request, 'order/confirm_order.html', {'form' : form, 'quote' : quote, 'quotelines' : lql})
    else:
        form = ConfirmOrderForm(request.POST)
        if form.is_valid():
            contact_id = xero_post_contact(form.cleaned_data, quote['Contact::reference'])
            invoice_id = xero_post_invoice(contact_id, form.cleaned_data['unique_reference_id'], quote, lql)
            ul.xero_contact_id = contact_id
            ul.xero_invoice_id = invoice_id
            ul.save()

            # payment gateway link
            url = xero_get_payment_gateway(ul.xero_invoice_id)
            return HttpResponseRedirect(url)

            #return render(request, 'order/order_received.html')
        else:
            return render(request, 'order/confirm_order.html', {'form' : form, 'quote' : quote, 'quotelines' : lql}) 
