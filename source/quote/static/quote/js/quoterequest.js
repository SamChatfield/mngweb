$(function() {

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
    $('#quote-unit-price').text('£' + unitPrice + " (standard)" + " / " + "£" + enhancedUnitPrice + " (enhanced)");
    $('#quote-total-price').text('£' + totalPrice);
    $("#quote-grand-total-price").text('£' + (totalPrice + totalEnhancedPrice));
  }

  setQuoteEstimate();
  $('#id_is_confidential,#id_num_dna_samples,#id_num_strain_samples,#id_num_enhanced_strain_samples').change(function() {
    setQuoteEstimate();
  });

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
  $('#id_bbsrc_code').parent().hide();
  $('#id_funding_type').change(function() {
    if ($(this).val() == 'BBSRC funded') {
      $('#id_bbsrc_code').parent().show();
      $('#id_is_confidential').prop('checked', false);
    } else if ($(this).val() == 'Industry') {
      $('#id_bbsrc_code').parent().hide();
      $('#id_is_confidential').prop('checked', true);
    } else {
      $('#id_bbsrc_code').parent().hide();
      $('#id_is_confidential').prop('checked', false);
    }
    setQuoteEstimate();
  });

  /*
  Disable strains and enhanced strains if samples are viral or fungal
  */
  $('#id_sample_types').change(function() {
    // Enable or disable strains and enhanced strains inputs and the note explaining this
    var disable = ($(this).val().includes('Viral') || $(this).val().includes('Fungi'))
    $('#id_num_strain_samples').prop('disabled', disable);
    $('#id_confirm_strain_bsl2').prop('disabled', disable);
    $('#id_num_enhanced_strain_samples').prop('disabled', disable);
    $('#id_confirm_enhanced_strain_bsl2').prop('disabled', disable);
    $('#viral_fungal_note').prop('hidden', !disable);

    // If inputs are disabled, also zero and uncheck them
    if (disable) {
      $('#id_num_strain_samples').val(0);
      $('#id_confirm_strain_bsl2').prop('checked', false);
      $('#id_num_enhanced_strain_samples').val(0);
      $('#id_confirm_enhanced_strain_bsl2').prop('checked', false);
    }
  });

  /*
  Replace plain label text with HTML versions for certain fields to increase usability
  */
  function replaceLabelText(field_sel, new_label) {
    $(field_sel).parent().contents().filter(function() {
      return this.nodeType === 3;
    }).first().replaceWith(new_label);
  }
  replaceLabelText('#id_is_confidential', 'Is confidential <span data-toggle="tooltip" title="Your data will never be uploaded into a public repository by MicrobesNG. See FAQ - Samples for more information."><i class="fa fa-question-circle"></i></span>');
  replaceLabelText('#id_confirm_strain_bsl2', 'Confirm that your strains comply with the <a class="criteria-link">strain submission criteria</a>');
  replaceLabelText('#id_confirm_enhanced_strain_bsl2', 'Confirm that your enhanced strains comply with the <a class="criteria-link">strain submission criteria</a>');
  $('[data-toggle="tooltip"]').tooltip();

  /*
  Strain submission criteria scrollIntoView link
  */
  $('.criteria-link').click(function (e) {
    e.preventDefault();
    $('.aside')[0].scrollIntoView();
    return false;
  });

  /*
  Comment box scrollIntoView link
  */
  $('.comments-link').click(function (e) {
    e.preventDefault();
    var commentBox = $('#id_comments')[0]
    commentBox.scrollIntoView();
    commentBox.focus();
    return false;
  });

  /*
  Show input for Conference (other) for where did you hear about us
  */
  $('#id_conference_other').parent().hide();
  $('#id_referral_type').change(function() {
    if ($(this).val() == 'Conference (other)') {
      // Show text field for conference (other)
      $('#id_conference_other').parent().show();
    } else {
      // Hide text field for conference (other)
      $('#id_conference_other').parent().hide();
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
