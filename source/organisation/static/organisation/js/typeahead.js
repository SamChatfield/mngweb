$(function() {

  var organisation = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/organisation/typeahead/'
  });

  function organisationWithDefaults(q, sync) {
    if (q === '') {
      sync(organisation.index.all())
    }

    else {
      organisation.search(q, sync);
    }
  }

  $('.organisation-typeahead input').typeahead({
    hint: true,
    highlight: true,
    minLength: 0
  },
  {
    name: 'organisation',
    source: organisationWithDefaults,
    limit: 100
  });
});