$(function() {


  // This function gets cookie with a given name
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

  /*
  The functions below will create a header with csrftoken
  */

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

});

// AJAX post
function ajax_post(form) {
  $.ajax({
    url : $(form).attr('action'),
    type : $(form).attr('method'),
    data : $(form).serialize(),

    success : function(json) {
      // Reset form, remove errors
      $(form).trigger("reset");
      $('.has-error', form).removeClass('has-error');
      $('.help-block', form).remove();

      // Display success message
      $('.alert-success', form).children('span').text(json.message);
      $('.alert-success', form).fadeIn(500).delay(4000).fadeOut(500);
    },

    error : function(xhr,errmsg,err) {
      var errors = JSON.parse(xhr.responseText);
      for (error in errors) {
        var id = '#id_' + error;
        var parent = $(id).parent('div');
        parent.addClass('has-error');
        if ($('.help-block', parent).length) {
          $('.help-block', parent).text(errors[error]);
        } else {
          parent.append('<span class="help-block">' + errors[error] + '</span>');
        }
      }
      console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
  });
};

// Submit post on submit
$('#contact-form').on('submit', function(event){
  event.preventDefault();
  ajax_post(this);
});

