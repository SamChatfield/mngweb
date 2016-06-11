$(function() {

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


  /*
  Ajax forms
  */

  // Create a header with csrftoken

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  var csrftoken = getCookie('csrftoken');

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }
  function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
      (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
      // or any other URL that isn't scheme relative or absolute i.e relative.
      !(/^(\/\/|http:|https:).*/.test(url));
  }

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
        // Send the token to same-origin, relative URLs only.
        // Send the token only if the method warrants CSRF protection
        // Using the CSRFToken value acquired earlier
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
      }
    }
  });

  // AJAX post
  function ajax_post(form) {
    // Remove errors before new request
    $('.has-error', form).removeClass('has-error');
    $('.help-block', form).remove();

    // Update button to show in-progress spinner
    $('button[type="submit"] i', form).addClass('fa-spin fa-spinner');

    // Make the ajax request
    $.ajax({
      url : $(form).attr('action'),
      type : $(form).attr('method'),
      data : $(form).serialize(),

      success : function(json) {
        $(form).trigger("reset");
      },

      error : function(xhr,errmsg,err) {
        console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        var json = JSON.parse(xhr.responseText);;
        if ('errors' in json) {
          for (error in json.errors) {
            var id = '#id_' + error;
            var parent = $(id, form).parent('div');
            parent.addClass('has-error');
            if ($('.help-block', parent).length) {
              $('.help-block', parent).text(json.errors[error]);
            } else {
              parent.append('<span class="help-block">' + json.errors[error] + '</span>');
            }
          }
        }
      },

      complete : function(xhr, status) {
        $('button[type="submit"] i', form).removeClass('fa-spin fa-spinner');
        var json = JSON.parse(xhr.responseText);
        $('.form-messages', form).empty(); // clear messages div
        if ('messages_html' in json) {
          $('.form-messages', form).html(json.messages_html);
        }
        $('.form-messages', form).children().hide().fadeIn(500).delay(4000).fadeOut(500);
      }
    });
  };

  // AJAX post on submit
  $(document).on('submit', '#contact-form', function(event){
    event.preventDefault();
    ajax_post(this);
  });

  $(document).on('submit', '#email-link-form', function(event){
    event.preventDefault();
    ajax_post(this);
  });

});
