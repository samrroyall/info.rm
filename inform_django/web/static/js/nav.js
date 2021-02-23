$(document).ready( function () {
    $("nav li.leagueNav div.firstRow a#leagueDropdown").click( function() {
        let current_display = $("li.leagueNav div.secondRow").css("display");
        console.log(current_display);
        if (current_display === "none") {
            $("nav li.leagueNav div.secondRow").css("display", "flex");
            $("nav li").css("height", "calc(90px + 1vw)");
        } else if (current_display === "flex") {
            $("nav li.leagueNav div.secondRow").css("display", "none");
            $("nav li").css("height", "calc(25px + 1vw)");
        } else {
            throw "leagueNav secondRow div has invalid display value";
        }
    });
});