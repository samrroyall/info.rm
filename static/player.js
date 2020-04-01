$(document).ready( function() {
  $("#player-season-select").change( function() {
    var season = $(this).val();
    var split_href = window.location.href.split("/");
    if (split_href[split_href.length - 1] == "per-90") {
      split_href[split_href.length - 2] = season;
    } else {
      split_href[split_href.length - 1] = season;
    }
    window.location.href = split_href.join("/");
  });
});
