$(function() {
  var organisation = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/organisation/typeahead/'
  });
  $('.organisation-typeahead input').typeahead({
    hint: true,
    highlight: true,
    minLength: 0
  },
  {
    name: 'organisation',
    source: organisation,
    limit: 10
  });
});