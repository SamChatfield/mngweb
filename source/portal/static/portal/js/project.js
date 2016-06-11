$(function() {
  var taxon = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/portal/taxon/search/'
  });
  $('.taxon-typeahead input').typeahead({
    hint: true,
    highlight: true,
    minLength: 0
  },
  {
    name: 'taxon',
    source: taxon,
    limit: 10,
    templates: {
      empty: '<div class="tt-suggestion">Start typing and choose the closest taxon</div>'
    }
  });
});