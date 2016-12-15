(function (mngweb, $) {
  'use strict';
  /*
  Password toggler
  */
  var PasswordToggler = function(element, field) {
    this.element = element;
    this.field = field;

    this.toggle();
  };

  PasswordToggler.prototype = {
    toggle: function() {
      var self = this;
      self.element.addEventListener('click', function() {
        if( self.element.checked ) {
          self.field.setAttribute('type', 'text');
        } else {
          self.field.setAttribute('type', 'password');
        }
      }, false);
    }
  };

  $(function() {
    /*
    Init. password show/hide togglers
    */
    $('.show-hide-password').each(function (i, e) {
      var checkbox = e;
      var pwd = $(checkbox).closest('form').find('.password-field > input')[0];
      new PasswordToggler(checkbox, pwd);
    });

    /*
    Signup form display email confirmation address.
    */
    $('#signup_form #id_email').on('blur', function (e) {
      var field = e.target,
          emailAddress = field.value,
          formGroup = $(field).parent('.form-group'),
          helpBlock = formGroup.find('.help-block');
      if (helpBlock.length === 0) {
        formGroup.append('<span class="help-block"></span>');
        helpBlock = formGroup.find('.help-block');
      }
      if (field.checkValidity()) {
        formGroup.removeClass('has-error');
        helpBlock.empty();
        $('#signup_email_message').removeClass('hidden').find('.confirm-email-address').text(emailAddress);
      } else {
        $('#signup_email_message').addClass('hidden');
        helpBlock.text('Please enter a valid email address.');
        formGroup.addClass('has-error');
      }
    });
  });

})(window.mngweb = window.mngweb || {}, jQuery);
