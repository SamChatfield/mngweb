(function (mngweb, $, undefined) {
  'use strict';

  var typeahead = mngweb.typeahead || {};

  function ebiPrepareRemoteQuery (q) {
    var tokens = q.split(' '),
        len = tokens.length,
        i,
        t;
    for (i = 0; i < len; i++) {
      t = tokens.shift();
      if (t.length >= 3) tokens.push(t + '*');
    }
    return tokens.join(' AND ');
  }

  typeahead.ebiTaxonomyBloodhound = new Bloodhound({
    datumTokenizer: function(d) { 
      return Bloodhound.tokenizers.whitespace(d.fields.name); 
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: '/taxon/ebi_typeahead/',
      prepare: function (query, settings) {
        settings.data = {
          query: ebiPrepareRemoteQuery(query),
          fields: 'name',
          format: 'json',
          size: 50
        };
        return settings;
      },
      transform: function (response) {
        return response.entries.sort(function (a, b) { return a.fields.name[0].localeCompare(b.fields.name[0]); });
      }
    }
  });

  // Legacy bloodhound instances for internal taxonomy
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
    $('.ebi-taxonomy-typeahead input').typeahead({
      hint: false,
      highlight: true,
      minLength: 3
    },
    {
      name: 'ebi-taxonomy',
      source: typeahead.ebiTaxonomyBloodhound,
      limit: Infinity,
      display: 'id',
      templates: {
        empty: [
          '<div class="tt-suggestion">',
            'Unable to find any match for that query in the EBI taxonomy',
          '</div>'
        ].join('\n'),
        suggestion: function (d) {
          return '<div>' + d.fields.name[0] + ' (<em>taxid: ' + d.id + ')</em></div>';
        }
      }
    });

    $('.taxon-typeahead input').typeahead({
      hint: true,
      highlight: true,
      minLength: 0
    },
    {
      name: 'taxon',
      source: typeahead.taxonomy,
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
      source: typeahead.taxonomyProkaryotes,
      limit: 10,
      templates: {
        empty: '<div class="tt-suggestion">Start typing and choose the closest taxon</div>'
      }
    });
  });

})(window.mngweb = window.mngweb || {}, jQuery);