// Stat arrows JS
function changeStat(stat, currPage, numPages, action) {
  if (action == "next") {
    $("." + stat + "_card_" + currPage.toString()).hide();
    $("." + stat + "_prev_" + currPage.toString()).hide();
    $("." + stat + "_next_" + currPage.toString()).hide();
    if (currPage != (numPages - 1)) {
      $("." + stat + "_card_" + (currPage + 1).toString()).show();
      $("." + stat + "_prev_" + (currPage + 1).toString()).show();
      $("." + stat + "_next_" + (currPage + 1).toString()).show();
    } else {
      $("." + stat + "_card_0").show();
      $("." + stat + "_prev_0").show();
      $("." + stat + "_next_0").show();
    }
  } else if (action == "prev") {
    $("." + stat + "_card_" + currPage.toString()).hide();
    $("." + stat + "_prev_" + currPage.toString()).hide();
    $("." + stat + "_next_" + currPage.toString()).hide();
    if (currPage != 0) {
      $("." + stat + "_card_" + (currPage - 1).toString()).show();
      $("." + stat + "_prev_" + (currPage - 1).toString()).show();
      $("." + stat + "_next_" + (currPage - 1).toString()).show();
    } else {
      $("." + stat + "_card_" + (numPages - 1).toString()).show();
      $("." + stat + "_prev_" + (numPages - 1).toString()).show();
      $("." + stat + "_next_" + (numPages - 1).toString()).show();
    }
  }
}
// Pagination JS
function changePage(stat, substat, page) {
  var i = 1;
  for (; i < 6; i++) {
     if (i != page) {
       $("div#" + stat + "_" + substat + "_page_" + i.toString()).hide();
       $("li#" + stat + "_" + substat + "_pagination_" + i.toString()).removeClass("active");
     } else {
       $("div#" + stat + "_" + substat + "_page_" + i.toString()).show();
       $("li#" + stat + "_" + substat + "_pagination_" + i.toString()).addClass("active");
     }
  }
}

// remove league div borders when navbar collapsed
function leagueBorders() {
  if ( $("#league-nav").is(":visible") ){
    $("#league-nav").addClass("border-left")
    $("#other-league-nav").addClass("border-left")
  } else {
    $("#league-nav").removeClass("border-left")
    $("#other-league-nav").removeClass("border-left")
  }
}

$(document).ready( function() {
  // check league div borders
  leagueBorders();
  $(window).resize( function() {
    leagueBorders();
  });
  // Per 90 Toggler and Season Dropdown JS
  $("#main_per90_toggle").change(function () {
      $(".cardList").toggleClass("hidden")
      $(".per90CardList").toggleClass("hidden")
  });
  $(function () {
    var split_loc = window.location.href.split("/");
    if (split_loc[split_loc.length - 1] == "per-90") {
      $("#player_per90_toggle").prop("checked", true);
    }
  });
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
  // Search Bar JS
  $("#nav-search").bind("keyup", function (evt) {
    var val = $(this).val().toString();
    var preSearch = window.location.href.split("/search/")[0];
    window.clearTimeout($(this).data("timeout"));
    $(this).data("timeout", setTimeout(function () {
      window.location.href = preSearch + "/search/" + "'" + val + "'";
    }, 750));
  });
});
