var PageViews = {
	init: function() {
		this.log(document.location.href);
		setTimeout('PageViews.postlogin()',2000);
	},
	log: function(addr) {
		$.post('/pageviews.json', {u: addr, referrer: document.referrer}, function(data) { 
			if (data['status'] == 'error') { alert(data.toString()); }
		});
	},
	postlogin: function() {
	    $.post('/postlogin.json', function(data) { 
			if (data['status'] == 'error') { alert(data.toString()); }
		});
	}
};
PageViews.init();