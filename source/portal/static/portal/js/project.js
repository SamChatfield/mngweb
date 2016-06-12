$(function() {
  var taxonProkaryotes = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/portal/api/taxon/prokaryotes/'
  });
  $('.taxon-pk-typeahead input').typeahead({
    hint: true,
    highlight: true,
    minLength: 0
  },
  {
    name: 'taxon-prokaryotes',
    source: taxonProkaryotes,
    limit: 10,
    templates: {
      empty: '<div class="tt-suggestion">Start typing and choose the closest taxon</div>'
    }
  });
});