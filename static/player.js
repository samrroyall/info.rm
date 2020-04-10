$(document).ready( function() {
  $(function() {
    $("#player_per90_toggle").change(function () {
      $(".playerStat").toggleClass("hidden");
      $(".playerStatPer90").toggleClass("hidden");
    });
  });
});
  
