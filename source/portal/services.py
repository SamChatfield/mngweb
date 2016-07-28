import requests

from datetime import datetime
from django.conf import settings
from django.utils.http import urlquote

from .forms import ProjectLineForm


PROJECT_DJANGO_TO_LIMSFM_MAP = {
    'project_id': 'project_id',
    'uuid': 'uuid',
    'address_country_iso2': 'Address::country_iso2',
    'all_content_received_date': 'all_content_received_date',
    'barcodes_sent_date': 'barcodes_sent_date',
    'creation_datetime': 'creation_host_timestamp',
    'contact_name_full': 'Contact::name_full',
    'contact_uuid': 'Contact::uuid',
    'data_sent_date': 'data_sent_date',
    'first_plate_barcode': 'projectcontainer_Container::reference',
    'meta_data_status': 'meta_data_status',
    'modal_queue_name': 'unstored_modal_queue_name',
    'projectline_count': 'unstored_projectline_count',
    'reference': 'reference',
    'results_path': 'results_path',
    'sample_sheet_url': 'sample_sheet_url',
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
    'container_position': 'Aliquot::unstored_container_position',
    'container_ref': 'Container::reference',
    'customers_ref': 'Sample::customers_ref',
    'dna_concentration_ng_ul': 'Aliquot::dna_concentration_ng_ul',
    'environmental_sample_type': 'Sample::environmental_sample_type',
    'further_details': 'Sample::further_details',
    'geo_country': 'Sample::geo_country_iso2_id',
    'geo_country_name': 'sample_Country::name',
    'geo_specific_location': 'Sample::geo_specific_location',
    'host_sample_type': 'Sample::host_sample_type',
    'host_taxon': 'Sample::host_taxon_id',
    'host_taxon_name': 'sample_Taxon#host::name',
    'lab_experiment_type': 'Sample::lab_experiment_type',
    'queue_name': 'Queue::name',
    'sample_ref': 'Sample::reference',
    'study_type': 'Sample::study_type',
    'taxon': 'Sample::taxon_id',
    'taxon_name': 'Taxon::name',
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


def project_from_limsfm(limsfm_project):
    project = {}

    for d, f in PROJECT_DJANGO_TO_LIMSFM_MAP.items():
        if f in limsfm_project:
            project[d] = limsfm_project[f]

    date_from_fmstr(project, 'all_content_received_date')
    datetime_from_fmstr(project, 'creation_datetime')
    date_from_fmstr(project, 'data_sent_date')

    if project['barcodes_sent_date']:
        date_from_fmstr(project, 'barcodes_sent_date')
    else:
        project['barcodes_sent_date'] = project['creation_datetime'].date()

    return project


def projectline_from_limsfm(limsfm_projectline):
    projectline = {}
    for d, f in PROJECTLINE_DJANGO_TO_LIMSFM_MAP.items():
        if f in limsfm_projectline:
            projectline[d] = limsfm_projectline[f]
    projectline['form'] = ProjectLineForm(initial=projectline)
    return projectline


def projectline_to_fm_dict(project_uuid, cleaned_data):
    """Convert dict data returned by a ProjectLineForm to a
       dict suitable to be used as a Filemaker RESTfm payload"""

    # Objects -> filemaker ids
    taxon = cleaned_data.pop('taxon_name', None)
    cleaned_data['taxon'] = taxon.fm_id if taxon else ''

    host_taxon = cleaned_data.pop('host_taxon_name', None)
    cleaned_data['host_taxon'] = host_taxon.fm_id if host_taxon else ''

    geo_country = cleaned_data.pop('geo_country_name', None)
    cleaned_data['geo_country'] = geo_country.iso2 if geo_country else ''

    # Construct dict
    fm_data = {}
    for k, v in cleaned_data.items():
        if k in PROJECTLINE_DJANGO_TO_LIMSFM_MAP:
            fm_data[PROJECTLINE_DJANGO_TO_LIMSFM_MAP[k]] = str(v) if v else ''
    fm_data['Project::uuid_validation'] = project_uuid

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


def limsfm_get_contact(uuid):
    # Get LIMSfm contact data
    response = limsfm_request(
        'layout/contact_api/%(field)s%(value)s' %
        {
            'field': urlquote('uuid==='),
            'value': urlquote(uuid)
        }, 'get')
    contact = response.json()['data'][0]

    # Get related projects
    response = limsfm_request('layout/project_api', 'get', {
        'RFMsF1': 'contact_id',
        'RFMsV1': contact['contact_id'],
        'RFMmax': 0
    })
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


def limsfm_get_project(uuid):
    """Return a Project dictionary, including ProjectLines, from LIMSfm"""

    uri = ('layout/project_api/%(field)s%(value)s' %
           {
               'field': urlquote('uuid==='),
               'value': urlquote(uuid)
           })
    project_response = limsfm_request(uri, 'get')
    project = project_from_limsfm(project_response.json()['data'][0])
    lines_response = limsfm_request('layout/projectline_api', 'get', {
        'RFMsF1': 'project_id',
        'RFMsV1': project['project_id'],
        'RFMmax': 0
    })
    projectlines_raw = lines_response.json()['data']

    # Map filemaker projectline keys to django keys
    project['modal_queue_matches'] = 0
    projectlines = []
    for pl in projectlines_raw:
        projectline = projectline_from_limsfm(pl)
        if projectline['queue_name'] == project['modal_queue_name']:
            project['modal_queue_matches'] += 1
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

    return project


def limsfm_update_projectline(project_uuid, projectline_uuid, cleaned_data):
    """Update a single LIMSfm ProjectLine"""

    json = {'data': [projectline_to_fm_dict(project_uuid, cleaned_data)]}
    uri = ('layout/projectline_api/%(field)s%(value)s' %
           {
               'field': urlquote('uuid==='),
               'value': urlquote(projectline_uuid)
           })
    return limsfm_request(uri, 'put', json=json)


def limsfm_bulk_update_projectlines(project_uuid, projectlines):
    """Update LIMSfm ProjectLines in bulk"""

    json = {'meta': [], 'data': []}

    for k, v in projectlines.items():
        json['meta'].append({'recordID': ('uuid===%s' % k)})
        json['data'].append(projectline_to_fm_dict(project_uuid, v))

    return limsfm_request('bulk/projectline_api', 'put', json=json)


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


def limsfm_email_project_links(email_address):
    """Call a script to email project links to contact"""
    uri = 'script/contact_email_project_links/REST'
    return limsfm_request(uri, 'get', params={'RFMscriptParam': email_address})
