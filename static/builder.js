$(document).ready(function() {
  // trigger custom stat dropdown
  $("#filter_button").click(function() {
    if ($("#custom_stat").hasClass("hidden")) {
      $("#custom_stat").removeClass("hidden");
    } else {
      $("#custom_stat").addClass("hidden");
    }
  });
  // add select option 
  $("#select_plus_1").click(function() {
    if ($("#select_div_2").hasClass("hidden")) {
      $("#select_div_2").removeClass("hidden");
      $("#select_per90_toggle_div_2").removeClass("hidden");
    } else {
      $("#select_div_2").addClass("hidden");
      $("#select_per90_toggle_div_2").addClass("hidden");
    }
  });
  $("#select_plus_2").click(function() {
    if ($("#select_div_3").hasClass("hidden")) {
      $("#select_div_3").removeClass("hidden");
      $("#select_per90_toggle_div_3").removeClass("hidden");
    } else {
      $("#select_div_3").addClass("hidden");
      $("#select_per90_toggle_div_3").addClass("hidden");
    }
  });
  $("#select_plus_3").click(function() {
    if ($("#select_div_4").hasClass("hidden")) {
      $("#select_div_4").removeClass("hidden");
      $("#select_per90_toggle_div_4").removeClass("hidden");
    } else {
      $("#select_div_4").addClass("hidden");
      $("#select_per90_toggle_div_4").addClass("hidden");
    }
  });
  // add filter by stat option
  $("#stat_plus_1".toString()).click(function() {
    if ($("#stat_div_2").hasClass("hidden")) {
      $("#stat_div_2").removeClass("hidden");
      $("#stat_expression_2").removeClass("hidden");
      $("#stat_per90_toggle_div_2").removeClass("hidden");
    } else {
      $("#stat_div_2").addClass("hidden");
      $("#stat_expression_2").addClass("hidden");
      $("#stat_per90_toggle_div_2").addClass("hidden");
    }
  });
  $("#stat_plus_2".toString()).click(function() {
    if ($("#stat_div_3").hasClass("hidden")) {
      $("#stat_div_3").removeClass("hidden");
      $("#stat_expression_3").removeClass("hidden");
      $("#stat_per90_toggle_div_3").removeClass("hidden");
    } else {
      $("#stat_div_3").addClass("hidden");
      $("#stat_expression_3").addClass("hidden");
      $("#stat_per90_toggle_div_3").addClass("hidden");
    }
  });
  $("#stat_plus_3".toString()).click(function() {
    if ($("#stat_div_4").hasClass("hidden")) {
      $("#stat_div_4").removeClass("hidden");
      $("#stat_expression_4").removeClass("hidden");
      $("#stat_per90_toggle_div_4").removeClass("hidden");
    } else {
      $("#stat_div_4").addClass("hidden");
      $("#stat_expression_4").addClass("hidden");
      $("#stat_per90_toggle_div_4").addClass("hidden");
    }
  });
  // trigger filter value options
  $("#filter_type").change(function() {
    var val = $(this).val();
    const types = ["age","club","league","minutes_played","nationality","position","stat"];
    if (val == "None") {
      for (const key of types) {
        $("#filter_" + key + "_div").addClass("hidden");
      }
    } else {
      $("#filter_" + val + "_div").removeClass("hidden");
    }
  });
  // update age value
  $("#age_op").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#age_input2_div").removeClass("hidden");
    } else {
      $("#age_input2_div").addClass("hidden");
    }
  });
  // minutes played between action
  $("#minutes_played_op").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#minutes_played_input2_div").removeClass("hidden");
    } else {
      $("#minutes_played_input2_div").addClass("hidden");
    }
  });
  // filter by stat between action
  $("#stat_cop_1").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#stat_input2_div_1").removeClass("hidden");
    } else {
      $("#stat_input2_div_1").addClass("hidden");
    }
  });
  $("#stat_cop_2").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#stat_input2_div_2").removeClass("hidden");
    } else {
      $("#stat_input2_div_2").addClass("hidden");
    }
  });
  $("#stat_cop_3").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#stat_input2_div_3").removeClass("hidden");
    } else {
      $("#stat_input2_div_3").addClass("hidden");
    }
  });
  $("#stat_cop_4").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#stat_input2_div_4").removeClass("hidden");
    } else {
      $("#stat_input2_div_4").addClass("hidden");
    }
  });
});

function getColumnName(statName, idName) {
  const lops = ["*","/","+","-"];
  // deal with per 90
  var per90 = false;
  var tempStatName = "";
  if (statName.includes("/(players.minutes_played/90.0)")) {
    per90 = true;
    tempStatName = statName.replace("/(players.minutes_played/90.0)", "");
  } else {
     tempStatName = statName;
  }
  var firstChar = tempStatName.substring(0,1);
  var lastChar = tempStatName.substring(tempStatName.length - 1, tempStatName.length);
  if ( (firstChar == "(") && (lastChar == ")") ) {
    // pull var out of the perens
    tempStatName = tempStatName.substring(1,tempStatName.length - 1);
  }
  // check for logical operators
  var col_lop = "";
  var cols;
  for (const lop of lops) {
    if (tempStatName.includes(lop)) {
      cols = tempStatName.split(lop);
      col_lop = lop;
      break;
    }
  }
  if (col_lop == "") {
    cols = [tempStatName];
  }

  // get new column name
  var result;
  if (cols.length == 1 && per90 == false) {
    // check length of column and underscores 
    if (cols[0].length <= 10) {
      result = cols[0];
    } else {
      result = cols[0].charAt(0).toUpperCase() + cols[0].substring(1,10) + ".";
    }
  } else if (cols.length == 2) {
    // get first char 
    result = cols[0][0].toUpperCase() + col_lop + cols[1][0].toUpperCase();
  }
  if (per90 == true) {
    result = result + "/90";
  }

  document.getElementById(idName).innerHTML = result;

}

