// Stat arrows JS
function changeStat(stat, currPage, action) {
  if (action == "next") {
    $("#" + stat + "_card_" + currPage.toString()).addClass("hidden");
    $("#" + stat + "_prev_" + currPage.toString()).addClass("hidden");
    $("#" + stat + "_next_" + currPage.toString()).addClass("hidden");
    if (currPage != 0) {
      $("#" + stat + "_card_" + (currPage - 1).toString()).removeClass("hidden");
      $("#" + stat + "_prev_" + (currPage - 1).toString()).removeClass("hidden");
      $("#" + stat + "_next_" + (currPage - 1).toString()).removeClass("hidden");
    } else { 
      $("#" + stat + "_card_2").removeClass("hidden");
      $("#" + stat + "_prev_2").removeClass("hidden");
      $("#" + stat + "_next_2").removeClass("hidden");
    }
  } else if (action == "prev") {
    $("#" + stat + "_card_" + currPage.toString()).addClass("hidden");
    $("#" + stat + "_prev_" + currPage.toString()).addClass("hidden");
    $("#" + stat + "_next_" + currPage.toString()).addClass("hidden");
    if (currPage != 2) {
      $("#" + stat + "_card_" + (currPage + 1).toString()).removeClass("hidden");
      $("#" + stat + "_prev_" + (currPage + 1).toString()).removeClass("hidden");
      $("#" + stat + "_next_" + (currPage + 1).toString()).removeClass("hidden");
    } else {
      $("#" + stat + "_card_0").removeClass("hidden");
      $("#" + stat + "_prev_0").removeClass("hidden");
      $("#" + stat + "_next_0").removeClass("hidden");
    }
  }
}
// Pagination JS
function changePage(stat, substat, page) {
  var i = 1;
  for (; i < 6; i++) {
     if (i != page) {
       $("div#" + stat + "_" + substat + "_page_" + i.toString()).addClass("hidden");
       $("li#" + stat + "_" + substat + "_pagination_" + i.toString()).removeClass("active");
     } else {
       $("div#" + stat + "_" + substat + "_page_" + i.toString()).removeClass("hidden");
       $("li#" + stat + "_" + substat + "_pagination_" + i.toString()).addClass("active");
     }
  }
}
// Per 90 Toggler and Season Dropdown JS
$(document).ready( function() {
  $(function () {
    var split_loc = window.location.href.split("/");
    if (split_loc[split_loc.length - 1] == "per-90") {
      $("#main_per90_toggle").prop("checked", true);
      $("#main_per90_toggle_label").toggleClass("text-secondary text-primary");
    }
  });
  $(function() {
    $("#main_per90_toggle").change(function () {
      $("#main_per90_toggle_label").toggleClass("text-secondary text-primary");
      var split_loc = window.location.href.split("/");
      if (split_loc[split_loc.length - 1] == "per-90") {
        window.location.href = window.location.href.split("/per-90")[0];
      } else {
        window.location.href = window.location.href + "/per-90";
      }
    });
  });
  $(function() {
    $("#season-select").change(function () {
      var val = $(this).val();
      var split_loc = window.location.href.split("/");
      if (split_loc[split_loc.length - 1] == "per-90") {
        split_loc[split_loc.length - 2] = val;
        window.location.href = split_loc.join("/") 
      } else {
        split_loc[split_loc.length - 1] = val;
        window.location.href = split_loc.join("/") 
      }
    });
  });
});
