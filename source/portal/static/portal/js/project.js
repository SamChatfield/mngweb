$(function() {

  // Tooltips init
  $('[data-toggle="tooltip"]').tooltip()

  // Modals init
  $('.modal').modal({show: false})

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
    var studyType = $('select[name="study_type"]', context).val();
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
    $('input[name="further_details"]', context).siblings('.help-block').text(fdHelpText);
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

  // AJAX post on projcetline submit
  $(document).on('submit', '.projectline-form', function(event){
    event.preventDefault();
    ajaxPost(this, false, function(form) {
      var editRow = $(form).closest('tr');
      var dataRow = $(form).closest('tr').prev('tr');
      editRow.collapse('hide');
      $('td.pl-taxon', dataRow).text($('input[name="taxon_name"]', form).val());
      $('td.pl-customers-ref', dataRow).text($('input[name="customers_ref"]', form).val());
      $('button.pl-edit-button', dataRow)
        .removeClass('btn-warning')
        .addClass('btn-success')
        .html('<i class="fa fa-check"></i> Saved');
    });
  });

  // AJAX sample sheet upload
  $('#sample_sheet_form').on('submit', function(event){
    event.preventDefault();
    $('#upload_progress_modal').modal('show');

    var formData = new FormData();
    var file = document.getElementById('id_file').files[0];
    formData.append('file', file, file.name);

    $.ajax({
      url: $(this).attr('action'),
      type: 'POST',
      data: formData,
      cache: false,
      dataType: 'json',
      processData: false, // Don't process the files
      contentType: false, // Set content type to false as jQuery will tell the server its a query string request

      success: function(json) {
        $('#upload_progress_modal').modal('hide');
        $('#sample_sheet_success_modal').modal('show');
        setTimeout(function () {
          window.location.href = json.redirect_url;
        }, 500)
      },

      error: function(xhr,errmsg,err) {
        console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        var json = JSON.parse(xhr.responseText);
        $('#upload_progress_modal').modal('hide');
        if ('messages' in json) {
          $('#sample_sheet_error_list').html('')
          var messages = json.messages;
          for (var i = 0; i < messages.length; i++) {
            var m = messages[i];
            $('#sample_sheet_error_list').append('<li>' + m.message + '</li>');
          }
        }
        $('#sample_sheet_errors_modal').modal('show');
      },
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