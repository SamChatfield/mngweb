(function (mngweb, $, undefined) {
  'use strict';

  var typeahead = mngweb.typeahead || {};

  typeahead.taxonomy = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/taxon/typeahead/'
  });

  typeahead.taxonomyProkaryotes = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/taxon/prokaryotes/typeahead/'
  });

  mngweb.typeahead = typeahead;

  /*
  jQuery document ready:
  */
  $(document).ready(function () {
    $('.taxon-typeahead input').typeahead({
      hint: true,
      highlight: true,
      minLength: 0
    },
    {
      name: 'taxon',
      source: mngweb.typeahead.taxonomy,
      limit: 10,
      templates: {
        empty: '<div class="tt-suggestion">Start typing and choose the closest taxon</div>'
      }
    });

    $('.taxon-pk-typeahead input').typeahead({
      hint: true,
      highlight: true,
      minLength: 0
    },
    {
      name: 'taxon-prokaryotes',
      source: mngweb.typeahead.taxonomyProkaryotes,
      limit: 10,
      templates: {
        empty: '<div class="tt-suggestion">Start typing and choose the closest taxon</div>'
      }
    });
  });

})(window.mngweb = window.mngweb || {}, jQuery);