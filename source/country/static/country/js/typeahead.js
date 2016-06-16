 $(function() {
  var countries = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/country/typeahead/'
  });
  $('.country-typeahead input').typeahead({
    hint: true,
    highlight: true,
    minLength: 0
  },
  {
    name: 'countries',
    source: countries,
    limit: 10,
    templates: {
      empty: '<div class="tt-suggestion">Start typing and choose a country</div>'
    }
  });
});