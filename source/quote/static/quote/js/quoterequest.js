$(function() {

  function checkEnhancedQuantity() {
    var quantity = $("#id_num_enhanced_strain_samples").val();
    if (quantity > 5) {
     $("#enhancedQuantityAlertModal").modal("show");
     $("#id_num_enhanced_strain_samples").val(5);
    }
  }

  /*
  Quote estimator
  */
  function setQuoteEstimate() {
    var isConfidential = $('#id_is_confidential').prop('checked');
    var fundingType = $('#id_funding_type').val();
    var dnaQty = parseInt($('#id_num_dna_samples').val());
    var strainQty = parseInt($('#id_num_strain_samples').val());
    var enhancedStrainQty = parseInt($("#id_num_enhanced_strain_samples").val())
    var totalQty;
    var unitPrice;
    var totalPrice;

    if (dnaQty != dnaQty) { dnaQty = 0; }
    if (strainQty != strainQty) { strainQty = 0; }
    if (enhancedStrainQty != enhancedStrainQty) { enhancedStrainQty = 0; }
    totalQty = dnaQty + strainQty;
    totalEnhancedQty = enhancedStrainQty;

    if (isConfidential) {
      unitPrice = 100;
    } else {
      switch (fundingType) {
        case 'Industry':
          unitPrice = 100;
          break;
        case 'Non-commercial':
          unitPrice = 70;
          break;
        default:
          unitPrice = 50;
      }
    }

    var CONFIDENTIAL_ENHANCED_RATE = 500;
    var ENHANCED_INDUSTRY_RATE = 500;
    var ENHANCED_NON_COMMERCIAL_RATE = 350;
    var STANDARD_ENHANCED_DATE = 250;


    if (isConfidential) {
      enhancedUnitPrice = CONFIDENTIAL_ENHANCED_RATE;
    } else {
      switch (fundingType) {
        case 'Industry':
          enhancedUnitPrice = ENHANCED_INDUSTRY_RATE;
          break;
          case 'Non-commercial':
          enhancedUnitPrice = ENHANCED_NON_COMMERCIAL_RATE;
          break;
        default:
          enhancedUnitPrice = STANDARD_ENHANCED_DATE;
          break;
      }
    }

    totalPrice = totalQty * unitPrice;
    totalEnhancedPrice = totalEnhancedQty * enhancedUnitPrice;
    $('#quote-total-qty').text(dnaQty + " (DNA)" + '\xa0\xa0\xa0' + "/" + "\xa0\xa0\xa0" + strainQty + " (strains)" + '\xa0\xa0\xa0' + "/" + '\xa0\xa0\xa0' + enhancedStrainQty + " (enhanced) = " + (totalQty + totalEnhancedQty))
    $('#quote-unit-price').text('£' + unitPrice + " (standard)" + " / " + "£" + enhancedUnitPrice + "(enhanced)");
    $('#quote-total-price').text('£' + totalPrice);
    $("#quote-grand-total-price").text('£' + (totalPrice + totalEnhancedPrice));
  }





  setQuoteEstimate();
  $('#id_is_confidential,#id_num_dna_samples,#id_num_strain_samples').change(function() {
    setQuoteEstimate();
  });

  $("#id_is_confidential,#id_num_enhanced_strain_samples").change(function() {
    checkEnhancedQuantity();
    setQuoteEstimate();
  })
  /*
  Show/hide principal investigator contact fields
  */
  $('#id_primary_contact_is_pi').on('change', function (e) {
    var piContactFields = $('.pi-contact-fields');
    if (e.target.checked) {
      piContactFields.hide();
    } else {
      piContactFields.show();
    }
  });

  /*
  Show/hide BBSRC grant code field
  */
  $('#id_funding_type').change(function() {
    if ($(this).val() == 'BBSRC funded') {
      $('#id_bbsrc_code').parent().show();
    } else {
      $('#id_bbsrc_code').parent().hide();
    }
    setQuoteEstimate();
  });

  /*
  Show/hide strain quantity, depending on country selection
  */
  $(".country-typeahead").on("typeahead:change", "input", function() {
    if ($(this).val().toLowerCase() == 'united kingdom') {
      $('#id_num_strain_samples').prop('disabled', false);
      $('#id_confirm_strain_bsl2').prop('disabled', false);
    } else {
      $('#id_num_strain_samples').val(0);
      $('#id_num_strain_samples').prop('disabled', true);
      $('#id_confirm_strain_bsl2').prop('disabled', true);
      setQuoteEstimate();
    }
  });

  /*
  Scroll to first error on page
  */
  (function() {
    var firstError = document.getElementsByClassName('has-error')[0];
    if (firstError !== undefined) {
      firstError.scrollIntoView();
    }
  })();

});
