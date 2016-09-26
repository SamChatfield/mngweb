$(function() {

  // Tooltips init
  $('[data-toggle="tooltip"]').tooltip()

  // Modals init
  $('.modal').modal({show: false})

  /*
  Popovers
  */

  // Initialise popovers, take content from hidden child divs
  $('[data-toggle="popover"]').popover({
    container: 'body',
    html : true,
    content: function() {
      var content = $(this).attr("data-popover-content");
      return $(content).children(".popover-body").html();
    },
    title: function() {
      var title = $(this).attr("data-popover-content");
      return $(title).children(".popover-heading").html();
    }
  });

  // Close popovers when clicking outside
  $('body').on('click', function (e) {
    $('[data-toggle="popover"]').each(function () {
        //the 'is' for buttons that trigger popups
        //the 'has' for icons within a button that triggers a popup
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });
  });
  
});
