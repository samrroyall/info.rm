$(document).ready( function() {
  $(function() {
    $("#player_per90_toggle").change(function () {
      $(".playerStat").toggleClass("hidden");
      $("player-stat-per90").toggleClass("hidden");
    });
  });
});
  
