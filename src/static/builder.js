$(document).ready(function() {
  // trigger custom stat dropdown
  $("#filter_button").click(function() {
    if ($("#customStat").hasClass("hidden")) {
      $("#customStat").removeClass("hidden");
    } else {
      $("#customStat").addClass("hidden");
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
  // trigger filter value options
  $("#filter_type").change(function() {
    var val = $(this).val();
    const types = ["age","club","league","minutes_played","nationality","position","stat"];
    if (val == "") {
      for (const key of types) {
        $("#filter_" + key + "_div").addClass("hidden");
        if (key == "stat") {
          $("#stat_field1_1").val("");
          $("#stat_field1_2").val("");
          $("#stat_field1_3").val("");
          $("#stat_field2_1").val("");
          $("#stat_field2_2").val("");
          $("#stat_field2_3").val("");
          $("#stat_lop_1").val("");
          $("#stat_lop_2").val("");
          $("#stat_lop_3").val("");
          $("#stat_cop_1").val("");
          $("#stat_cop_2").val("");
          $("#stat_cop_3").val("");
          $("#stat_input1_1").val("");
          $("#stat_input1_2").val("");
          $("#stat_input1_3").val("");
          $("#stat_input2_1").val("");
          $("#stat_input2_2").val("");
          $("#stat_input2_3").val("");
          $("#stat_per90_toggle_1").prop("checked", false);
          $("#stat_per90_toggle_2").prop("checked", false);
          $("#stat_per90_toggle_3").prop("checked", false);
        } if (key == "minutes_played") {
          $("#minutes_played_op").val("");
          $("#minutes_played_input1").val("");
          $("#minutes_played_input2").val("");
        } if (key == "age") {
          $("#age_op").val("");
          $("#age_input1").val("");
          $("#age_input2").val("");
        } if (key == "club") {
          $("#club_league_select").val("");
          $("#club_select").val("");
        } else {
          $("#" + key + "_select").val("");
        }
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
  $("#builder_form").validate( {
    rules: {
      "select": {
        required: true
      },
      "input": {
        number: true
      }
    },
    highlight: function (input) {
      $(input).addClass("is-invalid");
    },
    unhighlight: function (input) {
      $(input).removeClass("is-invalid");
    },
    errorPlacement: function (error, element) {
      $(element).next().append(error);
    }
  });
});

function getColumnAbbrev(col1, lop, col2) {
  var lookup = { shots: "S", shots_on: "SoT", shots_on_pct: "SoT%", goals: "G", goals_conceded: "GC", assists: "A", passes: "P", passes_key: "KP", passes_accuracy: "PA", tackles: "T", blocks: "B", interceptions: "I", duels: "DuT", duels_won: "DuW", duels_won_pct: "DuW%", dribbles_past: "DuP", dribbles_attempted: "DrA", dribbles_succeeded: "DrS",  dribbles_succeeded_pct: "DrS%", fouls_drawn: "FD", fouls_committed: "FC", cards_yellow: "YC", cards_red: "RC", penalties_won: "PW", penalties_committed: "PnC", penalties_success: "PnS", penalties_missed: "PnM", penalties_scored_pct: "PnS%", penalties_saved: "PnSa", minutes_played: "MP", games_appearances: "GA", games_started: "GS", games_bench: "GB", substitutions_in: "SbI", substitutions_out: "SbO", rating: "R"};
  var cols;
  if (lop) {
    cols = [col1, col2];
  } else {
    cols = [col1];
  }

  for (i=0; i < cols.length; i++) {
    cols[i] = lookup[cols[i]];
  }
  return cols.join(" " + lop + " ");
}

function getColumnName(statName, idName) {
  const lops = ["*","/","+","-"];
  // deal with per 90
  var per90 = false;
  var tempStatName = "";
  if (statName.includes("/(stats.minutes_played/90.0)")) {
    per90 = true;
    tempStatName = statName.replace("/(stats.minutes_played/90.0)", "");
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
  var cols = ["",""];
  for (const lop of lops) {
    if (tempStatName.includes(lop)) {
      var split_col = tempStatName.split(lop);
      cols[0] = split_col[0].split(".")[1]
      cols[1] = split_col[1].split(".")[1]
      col_lop = lop;
      break;
    }
  }
  if (col_lop == "") {
    cols[0] = tempStatName.split(".")[1];
  }

  var result = getColumnAbbrev(cols[0], col_lop, cols[1]);
  if (per90 == true) {
    result += " (/90)";
  }

  $("#" + idName).text(result);
}
