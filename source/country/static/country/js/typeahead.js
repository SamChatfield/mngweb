(function (mngweb, $, undefined) {
  'use strict';

  var typeahead = mngweb.typeahead || {};

  typeahead.countries = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/country/typeahead/'
  });

  typeahead.countriesShowAllOnEmpty = function (q, sync) {
    if (q === '') {
      sync(typeahead.countries.index.all());
    } else {
      typeahead.countries.search(q, sync);
    }
  };

  mngweb.typeahead = typeahead;

  /*
  jQuery document ready:
  */
  $(document).ready(function () {
    $('.country-typeahead input').typeahead({
      hint: true,
      highlight: true,
      minLength: 0
    },
    {
      name: 'countries',
      source: mngweb.typeahead.countriesShowAllOnEmpty,
      limit: 300
    });
  });

})(window.mngweb = window.mngweb || {}, jQuery);