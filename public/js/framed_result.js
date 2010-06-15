var FramedResult = {
  url: $('#data-url').text(),
  shareUrl: $('#data-result-url').text(),
  query: $('#data-query').text(),
  shareData: {},

  init: function() {
    this.sizeIframe();
    $(".fb-share-widget a").click(function(ev) { ev.preventDefault(); Results.fbShare(FramedResult.shareUrl, FramedResult.shareData) });
    $(window).resize(function() { FramedResult.sizeIframe(); });
      var url = '/share_counts?&urls[]=' + encodeURI(FramedResult.url);
   
    $.get(url, function(data) { 
      Results.populateShareCount($('.fb-share-count:first'), data[0]['total_count']); 
    });
    
    Results.fetchShareData(this.query, this.url, function(data) { FramedResult.shareData = data; });
  },
  sizeIframe: function() {
    $("#target_frame").height(($("#full_body_span").height()-79)+"px");
  }
};
FramedResult.init();