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
