$(function() {
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

  $('#id_study_type').change(function() {
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
});