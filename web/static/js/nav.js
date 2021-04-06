$(document).ready( () => {
    $("nav#mainNav li.burgerButton i").click( () => {
        const newHeight = 3*$(window).width()/100 + 175;
        const current_display = $("nav#collapsedNav").css("display");
        if (current_display === "none") {
            // fade collapsed nav content in  
            $("nav#collapsedNav").css("height", "0px");
            $("nav#collapsedNav").show();
            $("nav#collapsedNav").animate(
                {height: `${newHeight}px`}, 
                1000, 
                () => $("nav#collapsedNav").css("display", "flex")
            );
        } else {
            // fade collapsed nav content out
            $("nav#collapsedNav").animate({height: "0px"},  1000);
            setTimeout(() => $("nav#collapsedNav").hide(), 1000);
        }
    });
    $("nav#mainNav li.leagueNav div.firstRow i").click( () => {
        const originalHeight = $(window).width()/100 + 25;
        const newHeight = $(window).width()/100 + 90;
        let current_display = $("nav#mainNav li.leagueNav div.secondRow").css("display");
        if (current_display === "none") {
            // show up arrow
            $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-down-fill").hide();
            $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-up-fill").show();
            // fade second row in
            $("nav#mainNav li.leagueNav div.secondRow").show();
            $("nav#mainNav li").animate(
                {height: `${newHeight}px`},
                1000, 
                () => $("nav li.leagueNav div.secondRow").css("display", "flex") 
            );
        } else {
            // show down arrow
            $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-up-fill").hide();
            $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-down-fill").show();
            // fade second row out
            $("nav#mainNav li").animate({height: `${originalHeight}px`}, 1000);
            setTimeout(() => $("nav#mainNav li.leagueNav div.secondRow").hide(), 1000);
        }
    });
});