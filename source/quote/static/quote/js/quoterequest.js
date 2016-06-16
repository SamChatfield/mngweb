$(function() {
  function setQuoteEstimate() {
    var isConfidential = $("#id_is_confidential").prop('checked');
    var fundingType = $("#id_funding_type").val();
    var dnaQty = parseInt($("#id_num_dna_samples").val());
    var strainQty = parseInt($("#id_num_strain_samples").val());
    var totalQty = dnaQty + strainQty;
    if (isConfidential) {
      var unitPrice = 100;
    } else {
      switch (fundingType) {
        case 'Commercial':
          var unitPrice = 100;
          break;
        case 'Non-commercial':
          var unitPrice = 70;
          break;
        default:
          var unitPrice = 50;
      }
    }
    var totalPrice = totalQty * unitPrice;
    $("#quote-total-qty").text(totalQty);
    $("#quote-unit-price").text('£' + unitPrice);
    $("#quote-total-price").text('£' + totalPrice);
  }
  setQuoteEstimate();
  $('#id_funding_type,#id_is_confidential,#id_num_dna_samples,#id_num_strain_samples').change(function() {
    setQuoteEstimate();
  });
});