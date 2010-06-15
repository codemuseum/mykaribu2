// Place your application-specific JavaScript functions and classes here
// This file is automatically included by javascript_include_tag :defaults
function setIframeAd(query)
{
  $(".iframeAd").attr("src", "http://www.google.com/uds/GafsAds?q="
                     + encodeURI(query)
                     + "&hl=en&ad=w2&source=gcsc&qid=12821e3abd4855884&cx=004221970179818813180:lomxfldenpg");
}

var searchReady = false;
function executeSearch() 
{ 
  if(searchReady && queryTerm != null)
  { 
    customSearchControl.execute(queryTerm); 
    setIframeAd(queryTerm);
  }
}

var which = 0;
function setSearcher(sc, searcher)
{
  if(which == 0){
    $('.gsc-tabsArea').children().get(0).innerHTML = "Web";
    $('.gsc-tabsArea').children().get(2).onclick();
    which = 1;
  }else if(which == 1){
    if(searcher.results.length <= 0)
    { $('.gsc-tabsArea').children().get(4).onclick(); }
    which = 2;
  }else if(which == 2){
    if(searcher.results.length <= 0)
    { $('.gsc-tabsArea').children().get(0).onclick(); }
    which = 3;
  }
  jQuery.livequery.run();
  if(typeof(associateUsersWithLinks) == 'function'){associateUsersWithLinks();}
}

var customSearchControl = null;
function googleOnLoadCallback()
{
  customSearchControl = new google.search.CustomSearchControl('004221970179818813180:lomxfldenpg');
  customSearchControl.setResultSetSize(google.search.Search.LARGE_RESULTSET);

  customSearchControl.setSearchCompleteCallback(this, setSearcher);

  var options = new google.search.SearcherOptions();
  options.setExpandMode(google.search.SearchControl.EXPAND_MODE_OPEN);
  customSearchControl.addSearcher(new google.search.VideoSearch(), options);
  customSearchControl.addSearcher(new google.search.ImageSearch(), options);

  options = new google.search.DrawOptions();
  options.setDrawMode(google.search.SearchControl.DRAW_MODE_LINEAR);
  options.setSearchFormRoot('search-form-holder');
  customSearchControl.draw('cse-search-results', options);

  searchReady = true;
  setTimeout(executeSearch, 10);
}

function blink_in()
{ $("#blink_arrow").fadeIn(100, function() { setTimeout(blink_out, 250); }); }

function blink_out()
{ $("#blink_arrow").fadeOut(100, function(){ setTimeout(blink_in, 250); }); }

function bookmarkDone()
{
  FB.Facebook.apiClient.fql_query("SELECT bookmarked FROM permissions WHERE uid=" + FB.Facebook.apiClient.get_session().uid, 
  function(result, ex) {
    if(result[0]["bookmarked"] == "1")
    {
      $("#bookmark1").show();
      $("#bookmark2").show();
      $("#noBookmark2").hide();
      $("#noBookmark4").hide();
      $("#fanCompletePercent").html("100% Complete");
    }
  });
  $.ajax({'url': trigger_update_url });
}

function fanDone()
{
  FB.Facebook.apiClient.fql_query("SELECT uid FROM page_fan WHERE page_id=341655879017 AND uid=" 
    + FB.Facebook.apiClient.get_session().uid, 
  function(result, ex) {
    if(result != null && result[0] != null)
    {
      $("#fan1").show();
      $("#fan2").show();
      $("#noFan2").hide();
      $("#noFan4").hide();
    }
  });
  $.ajax({'url': trigger_update_url });
}

function makeSmallQuery()
{
  queryTerm = $("#smallSearchBox").val();
  if(queryTerm == null || queryTerm == "") { return false; }

  recordResultUrl = null;

  executeSearch();
  var url = gcreate_queries_url + "?query[query]=" + encodeURI(queryTerm) + "&query[private]=" 
    + $("input[name='query[private]']:checked").val();

  $.ajax({'url': url, 'dataType': 'script'});

  return false;
}

var lastText = "";
function spinRunning(item)
{ 
  var s = $('#searchBox');
  if(s.val() == lastText) { 
    s.val(item.text);
    $(".searchText").hide();
  }
  lastText = item.text;
}

function spinComplete(item)
{ $('#postSpinPopup').show(); }

function callSpin() {
  $('#searchBox').val("");
  lastText = "";
  spin();
}

function spin()
{ $("#flashWheel").get(0).spinWheel(); }

var wheelLoaded = false;
function wheelReady()
{ 
  wheelLoaded = true; 
  runWheel();
}

var items = [];
function runWheel()
{
  if(wheelLoaded && items.length > 0)
  {
    setTimeout(callItems, 10);
    setTimeout(spin, 3500);
  }
}

var loadDone = false;
function callItems() 
{ 
  if(loadDone) { return; }
  if($("#flashWheel").get(0).loadWheelItems)
  { $("#flashWheel").get(0).loadWheelItems(items, userItem); loadDone = true; }
  else
  { setTimeout(callItems, 1000); }
}

function sTrim(str) {
    return str.replace(/^\s*/, "").replace(/\s*$/, "");
}

function populateItemsArray(searchWords, friends)
{
  if(items.length > 0) { return; }
  for(var i = 0; i < 12; i++) {
    if ( i % 4 == 0 && friends.length > 0 )
    { items[i] = friends.splice(Math.floor(Math.random() * friends.length), 1)[0];  }
    else if( searchWords.length > 0 )
    {
      var word = searchWords.splice(Math.floor(Math.random() * searchWords.length), 1)[0]; 
      items[i] = {text: word, image: makeImageUrl(word), url: makeQueryUrl(word) };
    }
    else if( friends.length > 0 )
    { items[i] = friends.splice(Math.floor(Math.random() * friends.length), 1)[0];  }
    else
    { items[i] = defaults.splice(Math.floor(Math.random() * defaults.length), 1)[0];  }
  }
  runWheel();
}

function makeQueryUrl(term)
{ return gcreate_queries_url + "?query[query]=" + encodeURI(term); }

function makeImageUrl(term)
{ return google_image_url + "?term=" + encodeURI(term); }

var defaults = [
 {text: "Zorb", image: "/images/placeholders/zorb.jpg", url: makeQueryUrl("Zorb") },
 {text: "Hot Air Balloon Ride", image: "/images/placeholders/balloon.jpg", url: makeQueryUrl("Hot Air Ballon Ride") },
 {text: "Jennifer Lopez", image: "/images/placeholders/jennifer.jpg", url: makeQueryUrl("Jennifer Lopez") },
 {text: "Britney Spears", image: "/images/placeholders/britney.jpg", url: makeQueryUrl("Britney Spears") },
 {text: "Brad Pitt", image: "/images/placeholders/brad.jpg", url: makeQueryUrl("Brad Pitt") },
 {text: "iPad", image: "/images/placeholders/ipad.jpg", url: makeQueryUrl("iPad") },
 {text: "Digital Camera", image: "/images/placeholders/digital_camera.png", url: makeQueryUrl("Digital Camera") },
 {text: "Cute Koalas", image: "/images/placeholders/koala.jpg", url: makeQueryUrl("Cute Koalas") },
 {text: "Adorable Puppies", image: "/images/placeholders/cute-puppies.jpg", url: makeQueryUrl("Adorable Puppies") },
 {text: "Party Time!", image: "/images/placeholders/party-time.jpg", url: makeQueryUrl("Party Time!") },
 {text: "Surprise Present!", image: "/images/placeholders/woman_present.jpg", url: makeQueryUrl("Surprise Present!") },
 {text: "Fun Jewels", image: "/images/placeholders/necklace.jpg", url: makeQueryUrl("Fun Jewels") }
];

function getWheelData()
{
  setTimeout("populateItemsArray([], []);", 3000); //force populate with default if nothing in 3 sec
  try {
    var api = FB.Facebook.apiClient;
    var fields = ["quotes", "tv", "about_me", "music", "activities", "movies", "interests", "books"];
    var fields2 = ["quotes", "tv", "about_me", "music", "activities", "movies", "interests", "books", 
                   "first_name", "last_name", "pic"];

    var sequencer = new FB.BatchSequencer(); 
    var pendingFriendsResult = api.friends_get(null, sequencer);
    var pendingUserResult = api.users_getInfo([uid], fields2, sequencer); 
    var searchWords = [];

    sequencer.execute(function() {

      searchWords = []; 
      if(pendingUserResult.result && pendingUserResult.result[0]){
        var data = [];
        for(i in fields){ data.push(pendingUserResult.result[0][fields[i]].split(",")); }
        var joined = [];
        for(i in data){ joined = joined.concat(data[i]); }
        data = [];
        for(i in joined){ data.push(joined[i].split("\n")); }
        joined = [];
        for(i in data){ joined = joined.concat(data[i]); }
        data = [];
        for(i in joined){ data.push(sTrim(joined[i])); }
        for(i in data){ info = data[i]; if(info != null && info != "" && info != "," && info != "\n"){ searchWords.push(info); } }

        var userText = pendingUserResult.result[0]["first_name"] + " " + pendingUserResult.result[0]["last_name"];
        userItem = { text: userText,
                     image: (pendingUserResult.result[0]["pic"] || "/images/q_silhouette.gif"),
                     url: makeQueryUrl(userText) };
      }
  
      var selectedFriends = [];
      var allFriends = pendingFriendsResult.result;
      if(allFriends != null){
        for(var i=0; i< 12; i++){
          if(allFriends.length <= 0){ break; }
          selectedFriends.push(allFriends.splice(Math.floor(Math.random()*allFriends.length), 1)[0]);
        }
      }

      if(selectedFriends.length <= 0)
      { populateItemsArray(searchWords, []); }
      else {                             
        api.users_getInfo(selectedFriends, ["first_name", "last_name"], function(info, ex){
          var len = selectedFriends.length;
          selectedFriends = [];
          if(info != null){
            for(var i=0; i< len; i++){ 
              selectedFriends.push( { text: info[i]["first_name"] + " " + info[i]["last_name"], 
                                      image: "http://graph.facebook.com/"+info[i]["uid"]+"/picture?type=square", 
                                      url: makeQueryUrl(info[i]["first_name"] + " " + info[i]["last_name"]) } );
            }
          }
          populateItemsArray(searchWords, selectedFriends);
        });
      }
    });
  }catch(err){
    populateItemsArray([], []);
  }
}

var stopStream = false;
function makeQuery(){
  stopStream = true;
  queryTerm = $("#searchBox").val();
  if(queryTerm == null || queryTerm == "") { return false; }

  $("#makeQueryContainer").hide();
  $("#showQueryContainer").show();
  $("#smallSearchBox").val(queryTerm);
  $("#smallSearchBox").focus();

  executeSearch();

  $.ajax({'url': gcreate_queries_url + "?query[query]=" + encodeURI(queryTerm), 'dataType':'script'});

  return false;
}

function fillSearchStream(data){
  $('#offscreen').append(data);
  setTimeout(afterAppend, 500);
}

function afterAppend(){
  var el = $('#offscreen .streamReturn');
  if(el.length <= 0) { return; }
  var height = el.height() + 'px';
  el.css({'height': '0px'});
  $('#searchStream').prepend(el);
  el.animate({ 'height' : height }, 1000, function(){ 
    $(this).css({'height':'auto'}); 
    $('.streamReturn:last').remove();
    setTimeout(updateSearchStream, 500);
  });
}

function associateUsersWithLinks()
{
  for(i in userLinks)
  {
    if(!userLinks[i].added){
      var elements = $("a[href='"+userLinks[i].link+"']");
      if(elements.length > 0)
      {  
        elements.parent().parent().append(userLinks[i].html);
        userLinks[i].added = true;
      }
    }
  }

}
