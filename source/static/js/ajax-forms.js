(function (mngweb, $, undefined) {
  'use strict';

  var ajaxForms = mngweb.ajaxForms || {};

  /*
  ajaxForms: public methods, properties
  */

  ajaxForms.formPOST = function (form, resetOnSuccess, afterSuccess) {
    form = $(form);
    var teamContainer = form.closest('.team-container');

    // optional resetOnSuccess=true
    if (resetOnSuccess === undefined) {
      resetOnSuccess = true;
    }

    // Remove errors before new request
    form.find('.has-error').removeClass('has-error');
    form.find('.help-block').remove();

    // Update button to show in-progress spinner
    form.find('button[type="submit"] i').addClass('fa-spin fa-spinner');

    // Make the ajax request
    $.ajax({
      url: form.attr('action'),
      type: form.attr('method'),
      data: form.serialize(),

      success: function() {
        if (resetOnSuccess) {
          form.trigger('reset');
        }
        if (afterSuccess !== undefined) {
          afterSuccess(form);
        }
      },

      error: function(xhr) {
        var json, error, field, formGroup, helpBlock;
        console.log(xhr.status + ': ' + xhr.responseText); // provide a bit more info about the error to the console
        json = JSON.parse(xhr.responseText);
        if ('errors' in json) {
          for (error in json.errors) {
            field = form.find('[name="' + error + '"]');
            formGroup = field.closest('.form-group');
            formGroup.addClass('has-error');
            helpBlock = formGroup.find('.help-block');
            if (helpBlock.length) {
              helpBlock.text(json.errors[error]);
            } else {
              formGroup.append('<span class="help-block">' + json.errors[error] + '</span>');
            }
          }
        }
      },

      complete: function(xhr, status) {
        var json = JSON.parse(xhr.responseText);
        var messagesContainer = form.find('.form-messages');
        form.find('button[type="submit"] i').removeClass('fa-spin fa-spinner');
        if ('messages_html' in json) {
          messagesContainer.html(json.messages_html);
        }
        messagesContainer.children().hide().fadeIn(500).delay(10000).fadeOut(500);
      }
    });
  };

  mngweb.ajaxForms = ajaxForms;


  /*
  AJAX CSRF setup
  */

  var getCookie = function (name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  var csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  };

  var sameOrigin = function (url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = "//" + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + "/") ||
      (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + "/") ||
      // or any other URL that isn"t scheme relative or absolute i.e relative.
      !(/^(\/\/|http:|https:).*/.test(url));
  };

  var csrftoken = getCookie("csrftoken");

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
        // Send the token to same-origin, relative URLs only.
        // Send the token only if the method warrants CSRF protection
        // Using the CSRFToken value acquired earlier
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

})(window.mngweb = window.mngweb || {}, jQuery);