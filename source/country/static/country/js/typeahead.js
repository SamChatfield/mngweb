 $(function() {

  var countries = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/country/typeahead/'
  });

  function countriesShowAllOnEmpty(q, sync) {
    if (q === '') {
      sync(countries.index.all());
    }

    else {
      countries.search(q, sync);
    }
  }

  $('.country-typeahead input').typeahead({
    hint: true,
    highlight: true,
    minLength: 0
  },
  {
    name: 'countries',
    source: countriesShowAllOnEmpty,
    limit: 300
  });
});