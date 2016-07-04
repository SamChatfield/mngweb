from .forms import ProjectLineForm


SAMPLE_SHEET_COL_ORDER = [
    'well_alpha',
    'sample_ref',
    'customers_ref',
    'dna_concentration_ng_ul',
    'volume_ul',
    'taxon_name',
    'collection_day',
    'collection_month',
    'collection_year',
    'geo_country_name',
    'geo_specific_location',
    'lab_experiment_type',
    'further_details',
    'host_taxon_name',
    'host_sample_type',
    'further_details',
    'environmental_sample_type',
    'further_details',
]


def parse_sample_sheet(project, sheet):
    """Parse uploaded sample sheet data; return errors and updates"""

    projectlines = {}
    for pl in project['projectlines']:
        projectlines[pl['sample_ref']] = pl

    updates = {}
    errors = []

    for row in sheet.row_range()[6:102]:
        row_data = dict(zip(SAMPLE_SHEET_COL_ORDER, sheet.row[row]))
        sample_ref = str(row_data['sample_ref'])

        # Skip 'blank' rows
        if not row_data['customers_ref']:
            continue

        # Check sample ref in project
        if sample_ref not in projectlines:
            errors.append(
                {'row': row, 'message': "Barcode ID %(barcode)s is not "
                 "part of this project." %
                 {'row': row, 'barcode': sample_ref}})
            continue

        # Check well alpha has not shifted
        well_alpha = projectlines[sample_ref]['well_alpha']
        if well_alpha and well_alpha != row_data['well_alpha']:
            errors.append(
                {'row': row, 'message': "Barcode ID %(sample_ref)s should "
                 "correspond to plate well %(well)s." %
                 {'row': row, 'barcode': sample_ref, 'well': well_alpha}})
            continue

        # Determine 'study_type'
        if row_data.get('lab_experiment_type'):
            row_data['study_type'] = 'Lab'
        elif row_data.get('host_taxon_name'):
            row_data['study_type'] = 'Host'
        elif row_data.get('environmental_sample_type'):
            row_data['study_type'] = 'Environmental'
        else:
            errors.append(
                {'row': row, 'message': " Meta data is required in one "
                 "of the three coloured sections."})
            continue

        # Pass row data to form
        row_data['aliquottype_name'] = projectlines[sample_ref]['aliquottype_name']
        form = ProjectLineForm(row_data)
        if form.is_valid():
            uuid = projectlines[sample_ref]['uuid']
            updates[uuid] = form.cleaned_data
        else:
            for i, col in enumerate(form.errors):
                errors.append(
                    {'row': row, 'message': form.errors[col][0]})

    if not (errors or updates):
        errors.append({'row': 0, 'message': "No rows to update."})

    return {'errors': errors, 'updates': updates}
