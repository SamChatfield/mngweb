$(function() {
  function setQuoteEstimate() {
    var isConfidential = $('#id_is_confidential').prop('checked');
    var fundingType = $('#id_funding_type').val();
    var dnaQty = parseInt($('#id_num_dna_samples').val());
    var strainQty = parseInt($('#id_num_strain_samples').val());
    var totalQty = dnaQty + strainQty;
    var unitPrice;
    var totalPrice;

    if (isConfidential) {
      unitPrice = 100;
    } else {
      switch (fundingType) {
        case 'Commercial':
          unitPrice = 100;
          break;
        case 'Non-commercial':
          unitPrice = 70;
          break;
        default:
          unitPrice = 50;
      }
    }

    totalPrice = totalQty * unitPrice;
    $('#quote-total-qty').text(totalQty);
    $('#quote-unit-price').text('£' + unitPrice);
    $('#quote-total-price').text('£' + totalPrice);
  }
  setQuoteEstimate();
  $('#id_is_confidential,#id_num_dna_samples,#id_num_strain_samples').change(function() {
    setQuoteEstimate();
  });

  $('#id_funding_type').change(function() {
      if ($(this).val() == 'BBSRC funded') {
        $('#id_bbsrc_code').parent().show();
      } else {
        $('#id_bbsrc_code').parent().hide();
      }
      setQuoteEstimate();
  });

  // scroll to first error on page
  (function() {
    var firstError = document.getElementsByClassName('has-error')[0];
    if (firstError !== undefined) {
      firstError.scrollIntoView();
    }
  })();

});