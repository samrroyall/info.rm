function getColumnAbbrev (col1, lop, col2) {
  var lookup = { shots: "S", shots_on: "SoT", shots_on_pct: "SoT%", goals: "G", goals_conceded: "GC", assists: "A", passes: "P", passes_key: "KP", passes_accuracy: "PA", tackles: "T", blocks: "B", interceptions: "I", duels: "DuT", duels_won: "DuW", duels_won_pct: "DuW%", dribbles_past: "DuP", dribbles_attempted: "DrA", dribbles_succeeded: "DrS",  dribbles_succeeded_pct: "DrS%", fouls_drawn: "FD", fouls_committed: "FC", cards_yellow: "YC", cards_red: "RC", penalties_won: "PW", penalties_committed: "PnC", penalties_scored: "PnS", penalties_missed: "PnM", penalties_scored_pct: "PnS%", penalties_saved: "PnSa", minutes_played: "MP", games_appearances: "GA", games_started: "GS", games_bench: "GB", substitutions_in: "SbI", substitutions_out: "SbO", rating: "R"};
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

function getColumnName (statName, idName) {
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

$(document).ready( function() {
  // trigger custom stat dropdown
  $("#filter_button").click( function() {
    $("#custom-stat").toggle();
  });
  // add select option
  $("#select_plus_1").click( function() {
    $("#select_div_2").toggleClass("hidden");
    $("#select_per90_toggle_div_2").toggleClass("hidden");
  });
  $("#select_plus_2").click( function() {
      $("#select_div_3").toggleClass("hidden");
      $("#select_per90_toggle_div_3").toggleClass("hidden");
  });
  // add filter by stat option
  $("#stat_plus_1").click( function() {
    $("#stat_div_2").toggleClass("hidden");
    $("#stat_expression_2").toggleClass("hidden");
    $("#stat_per90_toggle_div_2").toggleClass("hidden");
  });
  $("#stat_plus_2").click( function() {
    $("#stat_div_3").toggleClass("hidden");
    $("#stat_expression_3").toggleClass("hidden");
    $("#stat_per90_toggle_div_3").toggleClass("hidden");
  });
  // trigger filter value options
  $("#filter_type").change(function() {
    var val = $(this).val();
    const keys = ["age","club","league","minutes_played","nationality","position","stat"];
    if (val == "") {
      for (const key of keys) {
        $("#filter_" + key + "_div").hide();
        if (key == "stat") {
          const stat_ids = ["#stat_field1","#stat_field2","#stat_lop","#stat_cop","#stat_input1","#stat_input2","#stat_per90_toggle"];
          for (const id in stat_ids) {
            for (var i = 1; i <= 3; i++) {
              var new_id = id+"_"+i.toString();
              if (id.equals("stat_per90_toggle")) {
                $(new_id).prop("checked", false);
              } else {
                $(new_id).val("");
              }
            }
          }
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
      $("#filter_" + val + "_div").show();
    }
  });
  // update age value
  $("#age_op").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#age_input2_div").show();
    } else {
      $("#age_input2_div").hide();
    }
  });
  // minutes played between action
  $("#minutes_played_op").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#minutes_played_input2_div").show();
    } else {
      $("#minutes_played_input2_div").hide();
    }
  });
  // filter by stat between action
  $("#stat_cop_1").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#stat_input2_div_1").show();
    } else {
      $("#stat_input2_div_1").hide();
    }
  });
  $("#stat_cop_2").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#stat_input2_div_2").show();
    } else {
      $("#stat_input2_div_2").hide();
    }
  });
  $("#stat_cop_3").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#stat_input2_div_3").show();
    } else {
      $("#stat_input2_div_3").hide();
    }
  });
  $("#stat_cop_4").change(function() {
    var val = $(this).val();
    if (val == "><") {
      $("#stat_input2_div_4").show();
    } else {
      $("#stat_input2_div_4").hide();
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
