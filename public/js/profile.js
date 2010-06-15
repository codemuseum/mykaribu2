var Profile = {
  fbid: $('#profile-fb-user-id').text(),
  insideFbCanvas: $('body').hasClass('inside-fb-canvas'),
  init: function() {
    this.loadFriends();
    this.observeAllQueries();
    // if (this.insideFbCanvas) { FB.Canvas.setSize(); }
  },
  loadFriends: function() {
    var friendsBox = $('#friends_box');
    if (!friendsBox[0]) { return; } // don't go looking for friends unless we have somewhere to put them
    $.get('/profiles/'+this.fbid+'/friends.json', function(rows) {
      var friendCount = 0;
      var reAuth = $('#friends_box_alt .re-auth-required');
      var noFriends = $('#friends_box_alt .no-friends');
      if (rows['error_code'] == 190) {  // bad auth token
        if (reAuth[0]) { friendsBox.html(reAuth.html()); }
        else { friendsBox.html(noFriends.html()); }
      }
      else if (rows.length == 0) { friendsBox.html(noFriends.html()); }
      else {
        var htm = '';
        for (i in rows) {
          htm += '<a class="friend" href="/profiles/'+rows[i].uid+'">' + 
            '<div class="img"><img src="http://graph.facebook.com/'+rows[i].uid+'/picture?type=square" width="50" height="50"/></div>' +
            '<div class="name">'+rows[i].name+'</div>' +
            '</a>';
        }
        friendsBox.html(htm);
        friendCount = rows.length;
      }
      $('#friends_count').html(friendCount);
    });
  },
  observeAllQueries: function() {
    $('.query-feed .query').each(function(i) { Profile.observeQuery($(this)); });
  },
  observeQuery: function(query) {
    this.observeAddComment(query.find('.add-comment'));
    query.find('.comment').each(function(i) { Profile.observeComment($(this)) });
  },
  observeComment: function(comment) {
    comment.find('a.remove').click(function(ev) {
      ev.stopPropagation(); ev.preventDefault();
      if (confirm("Are you sure you want to delete this comment?")) {
        var url = this.href + '.json';
        _gaq.push(['_trackPageview', url]);
        $.post(url, function(data) {
          if (data['status'] == 'error') { ErrorLogger.report(data.toString()); }
          else { comment.slideUp(function() { comment.remove(); }); }
        });
      }
      return false;
    });
  },
  observeAddComment: function(addBox) {
    var textarea = addBox.find('textarea');
    textarea.focus(function(ev) {
      if (this.value == this.getAttribute('placeholder')) { this.value = ''; }
      addBox.removeClass('placeholder');
    });
    textarea.blur(function(ev) {
      if (this.value == '' && !addBox.hasClass('login-required')) { Profile.resetNewCommentTextArea(addBox, $(this)); }
    });
    
    var frm = addBox.find('form');
    frm.submit(function(ev) {
      ev.stopPropagation(); ev.preventDefault();
      if (!addBox.hasClass('submitting')) {
        var url = frm[0].action + '.json';
        _gaq.push(['_trackPageview', url]);
        $.post(url, frm.serialize(), function(data) {
          if (data['status'] == 'error') { ErrorLogger.report(data.toString()); }
          else { Profile.insertNewComment(addBox, data['html']); }  
          Profile.resetNewCommentTextArea(addBox, textarea);
        });
        addBox.addClass('submitting');
      }
      return false;
    });
  },
  insertNewComment: function(addBox, html) {
    var newComment = $(html);
    newComment.css({'display': 'none'});
    newComment.insertBefore(addBox.siblings('.afc'));
    this.observeComment(newComment);
    newComment.slideDown();
  },
  resetNewCommentTextArea: function(addBox, textarea) {
    addBox.addClass('placeholder');
    textarea[0].value = textarea[0].getAttribute('placeholder');
    addBox.removeClass('submitting');
  }
};
Profile.init();