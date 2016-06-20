$(function() {

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

  hideMetaFields(this);

  $('select[name="study_type"]').change(function() {
      var context = $(this).parent().parent();
      var studyType = $(this).val();
      clearMetaFields(context);
      hideMetaFields(context);
      switch (studyType) {
        case 'lab':
          $('.meta-data-lab', context).show();
          var fdPlaceholder = $('#lab-fd-placeholder').text();
          $('#id_further_details', context).attr("placeholder", fdPlaceholder);
          $('.meta-data-further-details', context).attr("placeholder", fdPlaceholder).show();
          break;
        case 'host':
          $('.meta-data-host', context).show();
          var fdPlaceholder = $('#host-fd-placeholder').text();
          $('#id_further_details', context).attr("placeholder", fdPlaceholder);
          $('.meta-data-further-details', context).show();
          break;
        case 'environmental':
          $('.meta-data-environmental', context).show();
          var fdPlaceholder = $('#env-fd-placeholder').text();
          $('#id_further_details', context).attr("placeholder", fdPlaceholder);
          $('.meta-data-further-details', context).show();
          break;
      }
  });

  // AJAX post on submit
  $(document).on('submit', '.projectline-form', function(event){
    event.preventDefault();
    console.log('Submit');
    ajaxPost(this, false);
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