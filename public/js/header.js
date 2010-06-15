var Header = {
  searchScoreEl: $('#score_frame'),
  init: function() {
    this.displayCurrentUserSearchScore();
    // $(".shadow").textShadow(); // apply ie text shadow fixes -- this doesn't work with white text shadows, only black
  },
  displayCurrentUserSearchScore: function() {
    $("#n0").scrollTop(30*parseInt($('#n0-value').text()));
    $("#n1").scrollTop(30*parseInt($('#n1-value').text()));
    $("#n2").scrollTop(30*parseInt($('#n2-value').text()));
    this.searchScoreEl.fadeIn();
  },
  // getter and setter
  currentUserSearchScore: function(val) {
    if ((typeof val === 'undefined') || val == null) { return parseInt(this.searchScoreEl.text()); }
    
    $('#n0-value').html(val%10);
    $('#n1-value').html(Math.floor(val/10)%10);
    $('#n2-value').html(Math.floor(val/100)%10);

    this.searchScoreEl.fadeOut(function() { Header.displayCurrentUserSearchScore(); });
  },
  // old getter and setter
  // currentUserSearchScore: function(newScore) {
  //   if ((typeof newScore === 'undefined') || newScore == null) { return parseInt(this.searchScoreEl.text()); }
  //   else {
  //     this.searchScoreEl.fadeOut(function() {
  //       Header.searchScoreEl.html(Header.formatNumber(newScore));
  //       Header.searchScoreEl.fadeIn();
  //     });
  //   }
  // },
  formatNumber: function(number) {
    var nStr = number.toString() + '';
  	x = nStr.split('.');
  	x1 = x[0];
  	x2 = x.length > 1 ? '.' + x[1] : '';
  	var rgx = /(\d+)(\d{3})/;
  	while (rgx.test(x1)) { x1 = x1.replace(rgx, '$1' + ',' + '$2');	}
  	return x1 + x2;
  }
};
Header.init();