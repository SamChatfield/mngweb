import requests

from django.conf import settings
from django.utils.http import urlencode, urlquote

from .forms import ProjectLineForm


PROJECT_DJANGO_TO_LIMSFM_MAP = {
    'uuid': 'uuid',
    'all_content_received_date': 'all_content_received_date',
    'contact_name_full': 'Contact::name_full',
    'projectline_count': 'unstored_projectline_count',
    'queue_name': 'unstored_modal_queue_name',
    'reference': 'reference',
    'sample_sheet_url': 'sample_sheet_url',
    'wait_time_weeks': 'unstored_wait_time_weeks',
}

PROJECT_LIMSFM_TO_DJANGO_MAP = {
    v: k for k, v in PROJECT_DJANGO_TO_LIMSFM_MAP.items()}

PROJECTLINE_DJANGO_TO_LIMSFM_MAP = {
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


def limsfm_get_project(uuid):
    """Return a Project dictionary, with related ProjectLines, from LIMSfm"""

    # Make API calls to get raw project and projectline data
    project_url = (
        settings.RESTFM_BASE_URL +
        'layout/project_api.json?' +
        urlencode({
            'RFMkey': settings.RESTFM_KEY,
            'RFMsF1': 'uuid',
            'RFMsV1': '==' + uuid,
        })
    )
    api_response = requests.get(project_url, timeout=5)
    project_raw = api_response.json()['data'][0]

    projectline_url = (
        settings.RESTFM_BASE_URL +
        'layout/projectline_api.json?' +
        urlencode({
            'RFMkey': settings.RESTFM_KEY,
            'RFMsF1': 'project_id',
            'RFMsV1': project_raw['project_id'],
            'RFMmax': 0,
        })
    )
    api_response = requests.get(projectline_url, timeout=5)
    projectlines_raw = api_response.json()['data']

    # Map filemaker project keys to django keys
    project = {}
    for d, f in PROJECT_DJANGO_TO_LIMSFM_MAP.items():
        if f in project_raw:
            project[d] = project_raw[f]

    # Map filemaker projectline keys to django keys
    projectlines = []
    for pl in projectlines_raw:
        data = {}
        for d, f in PROJECTLINE_DJANGO_TO_LIMSFM_MAP.items():
            if f in pl:
                data[d] = pl[f]
        if data['customers_ref']:
            data['form'] = ProjectLineForm(initial=data)
        else:
            data['form'] = ProjectLineForm()
        projectlines.append(data)

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


def projectline_to_fm_dict(project_uuid, projectline):
    """Convert dict data returned by a ProjectLineForm to a
    dict suitable to be used as a Filemaker RESTfm payload"""

    # Objects -> filemaker ids
    taxon = projectline.pop('taxon_name', None)
    if taxon:
        projectline['taxon'] = taxon.fm_id

    host_taxon = projectline.pop('host_taxon_name', None)
    if host_taxon:
        projectline['host_taxon'] = host_taxon.fm_id

    geo_country = projectline.pop('geo_country_name', None)
    if geo_country:
        projectline['geo_country'] = geo_country.iso2

    # Construct dict
    data = {}
    for k, v in projectline.items():
        if k in PROJECTLINE_DJANGO_TO_LIMSFM_MAP:
            data[PROJECTLINE_DJANGO_TO_LIMSFM_MAP[k]] = str(v) if v else ''
    data['Project::uuid_validation'] = project_uuid

    return data


def limsfm_update_projectline(project_uuid, projectline):
    """Update a single LIMSfm ProjectLine"""
    url = (
        settings.RESTFM_BASE_URL +
        'layout/projectline_api/' +
        urlquote('Sample::reference===') +
        urlquote(projectline.pop('sample_ref')) + '.json?' +
        urlencode({
            'RFMkey': settings.RESTFM_KEY,
        })
    )

    payload = {'data': [projectline_to_fm_dict(project_uuid, projectline)]}

    return requests.put(url, json=payload, timeout=5)


def limsfm_bulk_update_projectlines(project_uuid, projectlines):
    """Update LIMSfm ProjectLines in bulk"""
    url = (
        "%(base)sbulk/projectline_api.json?%(args)s" %
        {
            'base': settings.RESTFM_BASE_URL,
            'args': urlencode({'RFMkey': settings.RESTFM_KEY})
        }
    )

    payload = {
        'meta': [],
        'data': []
    }

    for projectline in projectlines:
        payload['meta'].append(
            {
                'recordID': (
                    'Sample::reference===%s' %
                    projectline.pop('sample_ref')
                )
            }
        )
        payload['data'].append(
            projectline_to_fm_dict(project_uuid, projectline)
        )

    return requests.put(url, json=payload, timeout=30)


def limsfm_email_project_links(email_address):
    url = (
        "%(base)sscript/contact_email_project_links/REST.json?%(args)s" %
        {
            'base': settings.RESTFM_BASE_URL,
            'args': urlencode({'RFMkey': settings.RESTFM_KEY})
        }
    )

    return requests.get(url, timeout=5)
