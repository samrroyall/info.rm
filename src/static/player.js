$(document).ready( function() {
  $(function() {
    $("#player-per90-toggle").change(function () {
      $(".player-stat").toggleClass("hidden");
      $(".player-stat-per90").toggleClass("hidden");
    });
  });
});
  
