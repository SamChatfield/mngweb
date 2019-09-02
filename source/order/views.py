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
    print (quote_code)
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

def xero_post_contact(cleaned_data):
    credentials = PrivateCredentials(settings.XERO_CREDENTIALS, settings.XERO_PRIVATE_KEY)
    xero = Xero(credentials)

    name = "%s (%s %s)" % (cleaned_data['organisation'], cleaned_data['name_first'], cleaned_data['name_last'])

    contact = {
        'Addresses': [ { 'AddressType': 'POBOX',
                         'City': cleaned_data['city'],
                         'Country': cleaned_data['country'],
                         'PostalCode': cleaned_data['postcode'],
                         'Region': cleaned_data['region']}],
        'EmailAddress':  cleaned_data['email'],
        'Name':          name
    }
    results = xero.contacts.put(contact)
    contact = results[0]
    return contact['ContactID']

def xero_post_invoice(contact_id, unique_reference_id, quote, lines):
    credentials = PrivateCredentials(settings.XERO_CREDENTIALS, settings.XERO_PRIVATE_KEY)
    xero = Xero(credentials)

    today = date.today()
    due = date.today() + timedelta(days=30)

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
        'Reference': quote['reference'],
        'Status': 'DRAFT',
        'Type': 'ACCREC'
    }

    for line in lines:
         invoice['LineItems'].append({
             "Description" : line['description'],
             "Quantity" : line['quantity'],
             "UnitAmount" : line['price'],
             #"AccountCode" : line['service_id'],
             #TODO ItemCode
         })

    results = xero.invoices.put(invoice)
    print (results)
    invoice = results[0]
    return invoice['InvoiceID']

def confirm_order(request, uuid):
    ul = get_object_or_404(UniqueLink, pk=uuid)

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
            contact_id = xero_post_contact(form.cleaned_data)
            invoice_id = xero_post_invoice(contact_id, form.cleaned_data['unique_reference_id'], quote, lql)
            ul.xero_contact_id = contact_id
            ul.xero_invoice_id = invoice_id
            ul.save()            
            return HttpResponse('Thanks for your order!')
        else:
            return render(request, 'order/confirm_order.html', {'form' : form, 'quote' : quote, 'quotelines' : lql}) 
