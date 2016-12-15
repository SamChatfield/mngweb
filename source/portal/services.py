import json
import requests

from datetime import datetime
from django.conf import settings
from django.utils.http import urlquote

from urllib.parse import urljoin

from .forms import ProjectLineForm


PROJECT_DJANGO_TO_LIMSFM_MAP = {
    'project_id': 'project_id',
    'uuid': 'uuid',
    'address_country_iso2': 'Address::country_iso2',
    'all_content_received_date': 'all_content_received_date',
    'barcodes_sent_date': 'barcodes_sent_date',
    'contact_name_full': 'project_Contact#primary::name_full',
    'creation_datetime': 'creation_host_timestamp',
    'data_sent_date': 'data_sent_date',
    'ena_abstract': 'ena_abstract',
    'ena_title': 'ena_title',
    'first_plate_barcode': 'projectcontainer_Container::reference',
    'has_dna_samples': 'uc_has_dna_samples',
    'has_strain_samples': 'uc_has_strain_samples',
    'meta_data_status': 'meta_data_status',
    'modal_queue_matches': 'uc_modal_queue_matches',
    'modal_queue_name': 'unstored_modal_queue_name',
    'portal_login_required': 'portal_login_required',
    'projectline_count': 'unstored_projectline_count',
    'reference': 'reference',
    'results_path': 'results_path',
    'sample_sheet_url': 'sample_sheet_url',
    'submission_requirements_name': 'submission_requirements_name',
    'wait_time_weeks': 'unstored_wait_time_weeks',
}

PROJECT_LIMSFM_TO_DJANGO_MAP = {
    v: k for k, v in PROJECT_DJANGO_TO_LIMSFM_MAP.items()}

PROJECTLINE_DJANGO_TO_LIMSFM_MAP = {
    'uuid': 'uuid',
    'aliquottype_name': 'Aliquot::unstored_aliquottype_name',
    'collection_day': 'Sample::collection_day',
    'collection_month': 'Sample::collection_month',
    'collection_year': 'Sample::collection_year',
    'container_position': 'Aliquot::container_position',
    'container_ref': 'Container::reference',
    'customers_ref': 'Sample::customers_ref',
    'dna_concentration_ng_ul': 'Aliquot::dna_concentration_ng_ul',
    'environmental_sample_type': 'Sample::environmental_sample_type',
    'further_details': 'Sample::further_details',
    'geo_country': 'Sample::geo_country_iso2_id',
    'geo_country_name': 'sample_Country::name',
    'geo_specific_location': 'Sample::geo_specific_location',
    'host_sample_type': 'Sample::host_sample_type',
    'host_taxon_id': 'Sample::host_taxon_id',
    'host_taxon_name': 'Sample::host_taxon_name',
    'is_confidential': 'Sample::is_confidential',
    'lab_experiment_type': 'Sample::lab_experiment_type',
    'queue_name': 'Queue::name',
    'sample_ref': 'Sample::reference',
    'study_type': 'Sample::study_type',
    'taxon_id': 'Sample::taxon_id',
    'taxon_name': 'Sample::taxon_name',
    'volume_ul': 'Aliquot::volume_ul',
    'well_alpha': 'Aliquot::unstored_well_position_display',
}

PROJECTLINE_LIMSFM_TO_DJANGO_MAP = {
    v: k for k, v in PROJECTLINE_DJANGO_TO_LIMSFM_MAP.items()}


def date_from_fmstr(dct, key):
    """Convert a filemaker date string to a datetime.date object, in place"""
    if dct[key]:
        dct[key] = datetime.strptime(dct[key], '%m/%d/%Y')


def datetime_from_fmstr(dct, key):
    """Convert a filemaker date string to a datetime object, in place"""
    if dct[key]:
        dct[key] = datetime.strptime(dct[key], '%m/%d/%Y %H:%M:%S')


def bool_from_fmstr(dct, key):
    """Convert a filemaker boolean value, in place"""
    if dct[key]:
        dct[key] = bool(int(dct[key]))


def list_from_fmstr(dct, key):
    """Convert a filemaker return-separated list, in place"""
    if dct[key]:
        dct[key] = dct[key].split('\n')


def value_to_fm_type(value):
    if value is None:
        return ''
    if isinstance(value, (int, float)):
        return value
    return str(value)


def project_from_limsfm(limsfm_project):
    project = {}

    for d, f in PROJECT_DJANGO_TO_LIMSFM_MAP.items():
        if f in limsfm_project:
            project[d] = limsfm_project[f]

    date_from_fmstr(project, 'all_content_received_date')
    datetime_from_fmstr(project, 'creation_datetime')
    date_from_fmstr(project, 'data_sent_date')
    bool_from_fmstr(project, 'has_dna_samples')
    bool_from_fmstr(project, 'has_strain_samples')
    bool_from_fmstr(project, 'portal_login_required')

    if project['barcodes_sent_date']:
        date_from_fmstr(project, 'barcodes_sent_date')
    else:
        project['barcodes_sent_date'] = project['creation_datetime'].date()

    if project['results_path']:
        project['results_url'] = urljoin(
            settings.MNGRESULTS_BASE_URL,
            project['results_path'] + '/')
        project['results_url_secure'] = urljoin(
            settings.MNGRESULTS_BASE_URL_SECURE,
            project['results_path'] + '/')

    return project


def projectline_from_limsfm(limsfm_projectline):
    projectline = {}
    for d, f in PROJECTLINE_DJANGO_TO_LIMSFM_MAP.items():
        if f in limsfm_projectline:
            projectline[d] = limsfm_projectline[f]
    bool_from_fmstr(projectline, 'is_confidential')
    projectline['form'] = ProjectLineForm(initial=projectline)
    return projectline


def projectline_to_fm_dict(project_uuid, cleaned_data):
    """Convert dict data returned by a ProjectLineForm to a
       dict suitable to be used as a Filemaker RESTfm payload"""

    # Objects -> filemaker ids
    geo_country = cleaned_data.pop('geo_country_name', None)
    cleaned_data['geo_country'] = geo_country.iso2 if geo_country else ''

    # Construct dict
    fm_data = {}
    for k, v in cleaned_data.items():
        if k in PROJECTLINE_DJANGO_TO_LIMSFM_MAP:
            fm_data[PROJECTLINE_DJANGO_TO_LIMSFM_MAP[k]] = value_to_fm_type(v)
    fm_data['Project::uuid_validation'] = project_uuid
    fm_data['Sample::declared_dna_conc_ngul'] = fm_data['Aliquot::dna_concentration_ng_ul']

    return fm_data


def limsfm_request(rel_uri, method='get', params={}, json=None):
    """Send an API request to LIMSfm (RESTfm).
       Returns a response object or raises an exception"""

    params['RFMkey'] = settings.RESTFM_KEY
    uri = (
        "%(base)s%(rel_uri)s.json" %
        {'base': settings.RESTFM_BASE_URL, 'rel_uri': rel_uri}
    )
    s = requests.Session()
    prepped_request = requests.Request(
        method, uri, params=params, json=json).prepare()
    response = s.send(prepped_request, timeout=60)
    response.raise_for_status()

    return response


def limsfm_get_contact(email):
    # Get LIMSfm contact data
    response = limsfm_request(
        'layout/contact_api/%(field)s%(value)s' %
        {
            'field': urlquote('email_address==='),
            'value': urlquote(email)
        }, 'get')
    contact = response.json()['data'][0]

    # Get related projects
    try:
        response = limsfm_request('layout/project_api', 'get', {
            'RFMsF1': 'Contact::email_address',
            'RFMsV1': '="{}"'.format(email),
            'RFMmax': 0
        })
    except requests.HTTPError as e:
        if (e.response.status_code == 500 and
                e.response.headers['X-RESTfm-FM-Status'] == '401'):
            contact['projects'] = []  # no projects found for contact
        else:
            raise  # unexpected
    else:
        project_records = response.json()['data']
        contact['projects'] = []
        for record in project_records:
            contact['projects'].append(project_from_limsfm(record))

        contact['projects'].sort(
            key=lambda k: (
                0 - datetime.combine(
                    k['barcodes_sent_date'], datetime.min.time()).timestamp(),
                k['first_plate_barcode'],
                k['reference'],
            ))

    return contact


def limsfm_get_project_permissions(uuid):
    """
    Return a project permissions dictionary (lightweight, single api call).
    Can be merged with a full project dictionary via. dict.update()
    """
    permissions = {
        'uuid': uuid,
        'portal_login_required': False,
        'contacts': [],
    }
    response = limsfm_request('layout/project_contact_api', 'get', {
        'RFMsF1': 'Project::uuid',
        'RFMsV1': uuid,
        'RFMmax': 0
    })
    records = response.json()['data']

    permissions['portal_login_required'] = records[0]['Project::portal_login_required']
    bool_from_fmstr(permissions, 'portal_login_required')

    for r in response.json()['data']:
        c = {
            'uuid': r['Contact::uuid'],
            'email': r['Contact::email_address'],
            'is_primary': r['unstored_is_primary'],
            'name': r['Contact::name_full']
        }
        bool_from_fmstr(c, 'is_primary')
        permissions['contacts'].append(c)
        if c['is_primary']:
            permissions['primary_contact'] = c

    permissions['contacts'].sort(key=lambda c: (not c['is_primary'], c['name']))

    return permissions


def limsfm_get_project(uuid):
    """Return a Project dictionary, including ProjectLines, from LIMSfm"""

    # Get project
    uri = ('layout/project_api/%(field)s%(value)s' %
           {
               'field': urlquote('uuid==='),
               'value': urlquote(uuid)
           })
    project_response = limsfm_request(uri, 'get')
    project = project_from_limsfm(project_response.json()['data'][0])

    # Get project permissions
    project.update(limsfm_get_project_permissions(uuid))

    # Get project lines
    lines_response = limsfm_request('layout/projectline_api', 'get', {
        'RFMsF1': 'project_id',
        'RFMsV1': project['project_id'],
        'RFMmax': 0
    })
    projectlines_raw = lines_response.json()['data']

    # Map filemaker projectline keys to django keys
    projectlines = []
    for pl in projectlines_raw:
        projectline = projectline_from_limsfm(pl)
        projectlines.append(projectline)

    # Sort the projectlines and append to list project dict
    projectlines.sort(
        key=lambda k: (
            k['container_ref'],
            int(k['container_position'])
            if len(k['container_position']) else 0,
            k['sample_ref'],
        )
    )
    project['projectlines'] = projectlines

    # Additional logic
    project['show_results'] = True if project['results_path'] and project['data_sent_date'] else False
    project['is_confidential'] = any(pl['is_confidential'] for pl in projectlines)

    return project


def limsfm_update_project(uuid, cleaned_data):
    """Update a project record"""

    # Construct dict
    fm_data = {}
    for k, v in cleaned_data.items():
        if k in PROJECT_DJANGO_TO_LIMSFM_MAP:
            fm_data[PROJECT_DJANGO_TO_LIMSFM_MAP[k]] = value_to_fm_type(v)
    json = {'data': [fm_data]}

    uri = ('layout/project_api/%(field)s%(value)s' %
           {
               'field': urlquote('uuid==='),
               'value': urlquote(uuid)
           })
    return limsfm_request(uri, 'put', json=json)


def limsfm_update_projectline(project_uuid, projectline_uuid, cleaned_data):
    """Update a single LIMSfm ProjectLine"""

    json = {'data': [projectline_to_fm_dict(project_uuid, cleaned_data)]}
    uri = ('layout/projectline_api/%(field)s%(value)s' %
           {
               'field': urlquote('uuid==='),
               'value': urlquote(projectline_uuid)
           })
    update_response = limsfm_request(uri, 'put', json=json)
    return update_response


def limsfm_bulk_update_projectlines(project_uuid, projectlines):
    """Update LIMSfm ProjectLines in bulk"""

    json = {'meta': [], 'data': []}
    for k, v in projectlines.items():
        json['meta'].append({'recordID': ('uuid===%s' % k)})
        json['data'].append(projectline_to_fm_dict(project_uuid, v))
    update_response = limsfm_request('bulk/projectline_api', 'put', json=json)
    return update_response


def limsfm_project_auto_queue(project_uuid):
    """Call a script to auto queue project lines after data submission, where appropriate"""
    uri = 'script/project_auto_queue_after_data_submission/REST'
    return limsfm_request(uri, 'get', params={'RFMscriptParam': project_uuid})


def limsfm_get_taxonomy(data_set=None, q=None):
    """Return taxonomy as a list of dictionaries"""
    uri = ('layout/taxon_api')
    request_args = {'RFMmax': 0}
    if data_set:
        request_args['RFMsF1'] = 'data_set'
        request_args['RFMsV1'] = data_set
    if q:
        request_args['RFMsF1'] = 'name'
        request_args['RFMsV1'] = q
    response = limsfm_request(uri, 'get', request_args)

    return response.json()['data']


def limsfm_get_countries():
    """Return countries as a list of dictionaries"""
    uri = ('layout/country_api')
    request_args = {'RFMmax': 0}
    response = limsfm_request(uri, 'get', request_args)

    return response.json()['data']


def limsfm_get_organisations():
    """Return Organisations as a list of dictionaries"""
    uri = ('layout/organisation_api')
    request_args = {
        'RFMmax': 0,
        'RFMsF1': 'organisationtype_id',
        'RFMsV1': '1',
    }
    response = limsfm_request(uri, 'get', request_args)

    return response.json()['data']


def limsfm_email_project_links(email_address):
    """Call a script to email project links to contact"""
    uri = 'script/contact_email_project_links/REST'
    return limsfm_request(uri, 'get', params={'RFMscriptParam': email_address})


def limsfm_project_add_contact(project_uuid, cleaned_data):
    """Call a script to crate a new ProjecContact record"""
    uri = 'script/project_add_contact/project_contact_api'
    cleaned_data['project_uuid'] = project_uuid
    return limsfm_request(uri, 'get', params={'RFMscriptParam': json.dumps(cleaned_data)})


def limsfm_project_remove_contact(project_uuid, contact_uuid):
    """Call a script to delete a ProjecContact record"""
    uri = 'script/project_remove_contact/REST'
    param = {'project_uuid': project_uuid, 'contact_uuid': contact_uuid}
    return limsfm_request(uri, 'get', params={'RFMscriptParam': json.dumps(param)})


def limsfm_create_quote(form_data):
    """Call a script to create a new quote"""
    str_data = {}
    for k, v in form_data.items():
        if k == 'country':
            str_data[k] = v.iso2
        elif k == 'phone':
            str_data['phone_country_code'] = v.country_code
            str_data['phone_national_number'] = v.national_number
        else:
            str_data[k] = str(v)
    uri = 'script/quote_api_create/quote_api'
    response = limsfm_request(
        uri,
        'get',
        params={'RFMscriptParam': json.dumps(str_data)})
    quote_ref = response.json()['data'][0]['reference']
    return quote_ref
