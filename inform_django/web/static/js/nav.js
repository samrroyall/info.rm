$(document).ready( function () {
    $("nav#mainNav li.leagueNav div.firstRow i").click( function() {
        let current_display = $("nav#mainNav li.leagueNav div.secondRow").css("display");
        if (current_display === "none") {
            const newHeight = $(window).width()/100 + 90;
            // show up arrow
            $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-down-fill").hide();
            $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-up-fill").show();
            // fade second row in
            $("nav#mainNav li.leagueNav div.secondRow").fadeIn(1000);
            $("nav#mainNav li").animate({
                height: `${newHeight}px`,
            }, 1000, () => $("nav li.leagueNav div.secondRow").css("display", "flex") );
        } else {
            const newHeight = $(window).width()/100 + 25;
            // show down arrow
            $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-up-fill").hide();
            $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-down-fill").show();
            // fade second row out
            $("nav#mainNav li.leagueNav div.secondRow").fadeOut(1000);
            $("nav#mainNav li").animate({
                height: `${newHeight}px`, 
            }, 1000);
        }
    });
});