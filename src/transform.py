    

    def process_player(self, player):
        attributes = { 
            "uid", "player_id", "league", "team_id", "firstname", "lastname", "position", "age", "birth_date", 
            "nationality", "height", "weight", "rating", "captain", "shots", "shots_on", "shots_on_pct", 
            "goals", "goals_conceded", "assists", "passes", "passes_key", "passes_accuracy", "tackles", 
            "blocks", "interceptions", "duels", "duels_won", "duels_won_pct", "dribbles_attempted", 
            "dribbles_succeeded", "dribbles_succeeded_pct", "fouls_drawn", "fouls_committed", 
            "cards_red", "cards_second_yellow", "cards_straight_red", "penalties_won", 
            "penalties_committed", "penalties_success", "penalties_missed", "pentlties_scored_pct", 
            "penalties_saved", "minutes_played", "games_started", "substitutions_out", "games_bench"
        }

        # process player data
        if player.get("weight"):
             player["weight"] = float(player.get("weight").split(" ")[0]) * 0.393701
        else:
            player["weight"] = None
        if player.get("height"):
            player["height"] = float(player.get("height").split(" ")[0]) * 2.20462
        else:
            player["height"] = None
        if player.get("rating"):
            player["rating"] = float(player.get("rating"))
        else:
            player["rating"] = None
        if player.get("captain"):
            player["captain"] = bool(player.get("captain"))
        else:
            player["captain"] = None
        if player.get("birth_date"):
            player["birth_date"] = datetime.strptime(player.get("birth_date"), "%d/%m/%Y").date()
        else:
            player["birth_date"] = None
        if player.get("position"):
            player["position"] = player.get("position").lower()
        else:
            player["position"] = None
        # shots
        player["shots_on"] = player.get("shots").get("on")
        player["shots"] = player.get("shots").get("total")
        if player.get("shots") and player.get("shots") > 0:
            player["shots_on_pct"] = round(100.0 * player.get("shots_on") / player.get("shots"))
        else:
            player["shots_on_pct"] = None
        # goals
        player["goals_conceded"] = player.get("goals").get("conceded")
        player["assists"] = player.get("goals").get("assists")
        player["goals"] = player.get("goals").get("total")
        # passes
        player["passes_key"] = player.get("passes").get("key")
        player["passes_accuracy"] = player.get("passes").get("accuracy")
        player["passes"] = player.get("passes").get("total")
        # tackles
        player["blocks"] = player.get("tackles").get("blocks")
        player["interceptions"] = player.get("tackles").get("interceptions")
        player["tackles"] = player.get("tackles").get("total")
        # duels
        player["duels_won"] = player.get("duels").get("won")
        player["duels"] = player.get("duels").get("total")
        if player.get("duels") and player.get("duels") > 0:
            player["duels_won_pct"] = round(100.0 * player.get("duels_won") / player.get("duels"))
        else:
            player["duels_won_pct"] = None
        # dribbles
        player["dribbles_attempted"] = player.get("dribbles").get("attempted")
        player["dribbles_succeeded"] = player.get("dribbles").get("success")
        if player.get("dribbles_attempted") and player.get("dribbles_attempted") > 0:
            player["dribbles_succeeded_pct"] = round(100.0 * player.get("dribbles_succeeded") / 
                                                        player.get("dribbles_attempted"))
        else:
            player["dribbles_succeeded_pct"] = None
        # fouls
        player["fouls_drawn"] = player.get("fouls").get("drawn")
        player["fouls_committed"] = player.get("fouls").get("committed")
        # cards
        player["cards_yellow"] = player.get("cards").get("yellow")
        player["cards_red"] = player.get("cards").get("red")
        player["cards_second_yellow"] = player.get("cards").get("yellowred")
        player["cards_straight_red"] = player.get("cards_red") - player.get("cards_second_yellow") 
        # pentalties
        player["penalties_won"] = player.get("penalty").get("won")
        player["penalties_committed"] = player.get("penalty").get("commited") # [sic]
        player["penalties_saved"] = player.get("penalty").get("saved")
        player["penalties_scored"] = player.get("penalty").get("success")
        player["penalties_missed"] = player.get("penalty").get("missed")
        if player.get("penalties_scored_pct") and player.get("penalties_scored_pct") > 0:
            player["penalties_scored_pct"] = round(100.0 * player.get("penalties_scored") / 
                                                        (player.get("penalties_scored") + 
                                                        player.get("penalties_missed")))
        else:
            player["penalties_scored_pct"] = None
        # games
        player["games_appearances"] = player.get("games").get("appearences") # [sic]
        player["minutes_played"] = player.get("games").get("minutes_played") # [sic]
        player["games_started"] = player.get("games").get("lineups") # [sic]
        player["games_bench"] = player.get("substitutes").get("bench") # [sic]
        player["substitutions_in"] = player.get("substitutes").get("in")
        player["substitutions_out"] = player.get("substitutes").get("out")

        new_player = {}
        for k, v in player.items():
            if hasattr(self.orm_class, k):
                new_player[k] = v
        return new_player

