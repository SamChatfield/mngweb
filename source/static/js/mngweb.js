(function (mngweb, $, undefined) {
  'use strict';

  /*
  Signout links, use POST
  */
  $(document).on('click', '.signout-link', function (e) {
    e.preventDefault();
    $('#signout-form').submit();
  });

  /*
  AJAX form event handlers
  */
  $(document).on("submit", "#contact-form, #email-link-form", function(event){
    event.preventDefault();
    mngweb.ajaxForms.formPOST(this);
  });

  /*
  jQuery document ready:
  */
  $(document).ready(function () {

    // Tooltips init
    $("[data-toggle='tooltip']").tooltip();

    // Modals init
    $('.modal').modal({show: false});

    // Initialise popovers, take content from hidden child divs
    $('[data-toggle="popover"]').popover({
      container: 'body',
      html: true,
      content: function () {
        var content = $(this).attr('data-popover-content');
        return $(content).children('.popover-body').html();
      },
      title: function() {
        var title = $(this).attr('data-popover-content');
        return $(title).children('.popover-heading').html();
      }
    });

    // Close popovers when clicking outside
    $('body').on('click', function (e) {
      $('[data-popover-content="#project-tracker-popover-content"]').each(function () {
        //the "is" for buttons that trigger popups
        //the "has" for icons within a button that triggers a popup
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
          $(this).popover('hide');
        }
      });
    });

    // Cookie consent init
    window.cookieconsent.initialise({
      'palette': {
        'popup': {
          'background': '#575757',
          'text': '#ffffff'
        },
      },
      'theme': 'classic',
      'content': {
        'message': 'We use cookies to ensure you get the best experience on our website.',
        'dismiss': 'OK',
        'link': 'Privacy policy',
        'href': '/microbesng-faq#privacy-policy'
      }
    });

  });

})(window.mngweb = window.mngweb || {}, jQuery);
