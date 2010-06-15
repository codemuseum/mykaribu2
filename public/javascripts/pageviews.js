var PageViews = {
	init: function() {
		this.log(document.location.href);
	},
	log: function(addr) {
		$.post('/pageviews.json', {u: addr, referrer: document.referrer}, function(data) { 
			if (data['status'] == 'error') { alert(data.toString()); }
		});
	}
};
PageViews.init();