$(function() {
  /*
  Quote estimator
  */
  function setQuoteEstimate() {
    var isConfidential = $('#id_is_confidential').prop('checked');
    var fundingType = $('#id_funding_type').val();
    var dnaQty = parseInt($('#id_num_dna_samples').val());
    var strainQty = parseInt($('#id_num_strain_samples').val());
    // var enhancedStrainQty = parseInt($("#id_num_enhanced_strain_samples").val())
    var totalQty;
    var unitPrice;
    var totalPrice;

    if (dnaQty != dnaQty) { dnaQty = 0; }
    if (strainQty != strainQty) { strainQty = 0; }
    // if (enhancedStrainQty != enhancedStrainQty) { enhancedStrainQty = 0; }
    totalQty = dnaQty + strainQty;
    // totalEnhancedQty = enhancedStrainQty;

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
          break;
      }
    }

    // if (isConfidential) {
    //   enhancedUnitPrice = "<CONFIDENTIAL_ENHANCED_RATE>";
    // } else {
    //   switch (fundingType) {
    //     case 'Industry':
    //       enhancedUnitPrice = "<ENHANCED_INDUSTRY_RATE>";
    //       break;
    //       case 'Non-commercial':
    //       enhancedUnitPrice = "<ENHANCED_NON_COMMERCIAL_RATE>";
    //       break;
    //     default:
    //       enhancedUnitPrice = "<STANDARD_ENHANCED_DATE>";
    //       break;
    //   }
    // }

    totalPrice = totalQty * unitPrice;
    // totalEnhancedPrice = totalEnhancedQty * enhancedUnitPrice;
    $('#quote-total-qty').text(totalQty);
    $('#quote-unit-price').text('£' + unitPrice);
    $('#quote-total-price').text('£' + totalPrice);
    // $("#quote-grand-total-price").text('£' + (totalPrice + totalEnhancedPrice));
    $("#quote-grand-total-price").text('£' + totalPrice);
  }




  function setEnhancedQuoteEstimate() {
    var isConfidential = $('#id_is_confidential').prop('checked');
    var fundingType = $('#id_funding_type').val();
    var strainQty = parseInt($('#id_num_enhanced_strain_samples').val());
    var totalQty;
    var unitPrice;
    var totalPrice;

    totalQty = strainQty;

    if (isConfidential) {
      unitPrice = "<CONFIDENTIAL_ENHANCED_RATE>";
    } else {
      switch(fundingType) {
        case 'Industry':
          unitPrice = "<INDUSTRY_ENHANCED_RATE>";
          break;
        case "Non-commercial":
          unitPrice = "<NON-COMMERCIAL_ENHANCED_RATE>";
          break;
        default:
          unitPrice = "<STANDARD_ENHANCED_RATE>";
          break;
      }
    }

    totalPrice = totalQty * unitPrice;
    $('#quote-total-enhanced-qty').text(totalQty);
    $('#quote-unit-enhanced-price').text('£' + unitPrice);
    $('#quote-total-enhanced-price').text('£' + totalPrice);

  }


  setQuoteEstimate();
  setEnhancedQuoteEstimate();
  $('#id_is_confidential,#id_num_dna_samples,#id_num_strain_samples').change(function() {
    setQuoteEstimate();
  });

  $("#id_is_confidential,#num_enhanced_strain_samples").change(function() {
    setEnhancedQuoteEstimate();
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
