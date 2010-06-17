var Home = {
  nextPage: window.location.href,
  loggedIn: $('body').hasClass('logged-in'),
  init: function() {
    if (!this.loggedIn) { this.observePageForLoginEvents(); }
    // this.trackPageView(window.location.href); // Taken over by pageviews.js
    this.showProfileNoticeIfNecessary();
  },
  observePageForLoginEvents: function() {
    $('a.preset-query-box').click(function(ev) { 
      ev.preventDefault();
      var a = this;
      Home.nextPage = a.href;
      Home.fbLoginPrompt(function() { window.location = Home.nextPage; });
    });
    
    $('form').submit(function(ev) {
      if (!Home.loggedIn) {
        ev.preventDefault();
        var frm = this;
        Home.fbLoginPrompt(function() { frm.submit(); });
      }
    });
  },
  showProfileNoticeIfNecessary: function() {
    var noticeBox = $('.display-profile-generated-notice');
    if (noticeBox[0]) {
      $.facebox(noticeBox.html());
      noticeBox.remove();
    }
  },
  fbLoginPrompt: function(onSuccess) {
    Home.trackPageView('/view-fb-allow-prompt');
    FB.login(function(response) {
      if (response.session) {
        if (response.perms) {  // perms is a comma separated list
          Home.trackPageView('/allowed-fb-allow-prompt');
          Home.loggedIn = true; 
          onSuccess(); 
        } 
        else {  // user is logged in, but did not grant any permissions
          Home.trackPageView('/allowed-but-no-permissions-fb-allow-prompt');
          Home.loggedIn = true; 
          onSuccess(); 
        }
      }
      else { 
        Home.trackPageView('/disallowed-fb-allow-prompt');
        Home.loggedIn = false; 
        alert('Oops!  We need you to login to do that =\\'); 
        window.location.reload();
      } // user is not logged in
    }, {perms:'publish_stream'});
  },
  fetchNewCredentials: function() {
    this.fbLoginPrompt(function(){ Home.setNewCredentials(); });
  },
  setNewCredentials: function() {
    $.post('/credentials.json', function(data) {
      if (data['status'] == 'error') { ErrorLogger.report(data.toString()); }
      window.location.reload();
    });
  },
  trackPageView: function(url) {
    PageViews.log(url); // Use New Library
  },
  blurSearchBox: function() {
    if ($('#search_edit')[0].value == '') { $('#search_hint').fadeIn(); }
  },
  focusSearchBox: function() {
    $('#search_hint').fadeOut();
  },
  blurPromptSearchBox: function() {
    var input = $('#q');
    if (input[0].value == '') { input.addClass('placeholder'); input[0].value = 'Type something.';  }
  },
  focusPromptSearchBox: function() {
    var input = $('#q');
    if (input.hasClass('placeholder')) { input.removeClass('placeholder'); input[0].value = '';  }
  }
};
Home.init();