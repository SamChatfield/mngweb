$(function() {

  // Tooltips
  $('[data-toggle="tooltip"]').tooltip()

  // Show/hide appropriate meta-data fields
  function hideMetaFields(context) {
    $('.meta-data-lab', context).hide();
    $('.meta-data-host', context).hide();
    $('.meta-data-environmental', context).hide();
    $('.meta-data-further-details', context).hide();
  }

  function clearMetaFields(context) {
    $('.meta-data-lab input', context).val('');
    $('.meta-data-host input', context).val('');
    $('.meta-data-environmental input', context).val('');
  }

  function showMetaFields(context) {
    var studyType = $('#id_study_type', context).val();
    hideMetaFields(context);
    switch (studyType) {
      case 'Lab':
        $('.meta-data-lab', context).show();
        $('.meta-data-further-details', context).show();
        var fdHelpText = $('#lab-fd-help-text').text();
        break;
      case 'Host':
        $('.meta-data-host', context).show();
        $('.meta-data-further-details', context).show();
        var fdHelpText = $('#host-fd-help-text').text();
        break;
      case 'Environmental':
        $('.meta-data-environmental', context).show();
        $('.meta-data-further-details', context).show();
        var fdHelpText = $('#env-fd-help-text').text();
        break;
    }
    $('#id_further_details', context).siblings('.help-block').text(fdHelpText);
  }

  $('select[name="study_type"]').each(function() {
      var context = $(this).parent().parent();
      showMetaFields(context);
  });

  $('select[name="study_type"]').change(function() {
      var context = $(this).parent().parent();
      clearMetaFields(context);
      showMetaFields(context);
  });

  // AJAX post on submit
  $(document).on('submit', '.projectline-form', function(event){
    event.preventDefault();
    console.log('Submit');
    ajaxPost(this, false, function(form) {
      var editRow = $(form).closest('tr');
      var dataRow = $(form).closest('tr').prev('tr');
      editRow.collapse('hide');
      $('td.pl-taxon', dataRow).text($('#id_taxon', form).val());
      $('td.pl-customers-ref', dataRow).text($('#id_customers_ref', form).val());
      $('button.pl-edit-button', dataRow)
        .removeClass('btn-warning')
        .addClass('btn-success')
        .html('<i class="fa fa-check"></i> Saved');
    });
  });

  // EnvironmentalSampleType typeahead
  var envSampleTypes = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/portal/environmentalsampletype/typeahead/'
  });
  function envSampleTypesWithDefaults(q, sync) {
    if (q === '') {
      sync(envSampleTypes.index.all());
    }

    else {
      envSampleTypes.search(q, sync);
    }
  }
  $('.environmentalsampletype-typeahead input').typeahead({
    hint: true,
    highlight: true,
    minLength: 0
  },
  {
    name: 'envSampleTypes',
    limit: Infinity,
    source: envSampleTypesWithDefaults,
  });

  // EnvironmentalSampleType typeahead
  var hostSampleTypes = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/portal/hostsampletype/typeahead/'
  });
  function hostSampleTypesWithDefaults(q, sync) {
    if (q === '') {
      sync(hostSampleTypes.index.all());
    }

    else {
      hostSampleTypes.search(q, sync);
    }
  }
  $('.hostsampletype-typeahead input').typeahead({
    hint: true,
    highlight: true,
    minLength: 0
  },
  {
    name: 'hostSampleTypes',
    limit: Infinity,
    source: hostSampleTypesWithDefaults,
  });

});