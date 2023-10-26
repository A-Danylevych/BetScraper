import json
import scrapy

from betscraper.items import BetscraperItem


class DraftkingsspiderSpider(scrapy.Spider):
    name = "draftkingsspider"
    allowed_domains = ["sportsbook.draftkings.com"]
    start_urls = ["https://sportsbook.draftkings.com/sports/soccer",
                  "https://sportsbook.draftkings.com/sports/basketball",
                  "https://sportsbook.draftkings.com/sports/football",
                  "https://sportsbook.draftkings.com/sports/tennis",
                  "https://sportsbook.draftkings.com/sports/baseball",
                  "https://sportsbook.draftkings.com/sports/boxing"]
    base_url = "https://sportsbook.draftkings.com"
    api_url = "https://sportsbook.draftkings.com/sites/US-SB/api/v3/event/"

    def parse(self, response):
        leagues = response.css("a.league-link__link")
        game = response.url.split("/")[-1]
        for league in leagues:
            league_url = self.base_url + league.css("::attr(href)").get()
            yield response.follow(league_url, callback=self.parse_league, cb_kwargs={'game': game})

    def parse_league(self, response, game):
        matches = response.css("a.sportsbook-event-accordion__title") or response.css("a.event-cell-link::attr(href)").getall()

        for match in matches:
            match_id = match.split("/")[-1] if isinstance(match, str) else match.css("::attr(href)").get().split("/")[-1]
            yield response.follow(f"{self.api_url}{match_id}?format=json", callback=self.parse_match, cb_kwargs={'game': game})

    def parse_match(self, response, game):
        json_data = json.loads(response.text)
        game_data = json_data.get("event", {})
        league = game_data.get("eventGroupName", "")
        team_1 = game_data.get("teamName1", "")
        team_2 = game_data.get("teamName2", "")
        date = game_data.get("startDate", "")
        if team_1 == "" or team_2 == "":
            return
        alliases_team_1 = set()
        alliases_team_2 = set()
        odds = []

        game_id = "^".join([game, format_string(league), format_string(team_1), format_string(team_2), date])

        categories = json_data.get("eventCategories", [])

        for category in categories:
            categoryId = category["categoryId"]
            if categoryId == -2:
                continue
            for market in category.get("componentizedOffers", []):
                for offers in market.get("offers", []):
                    for offer in offers:
                        market_name = offer.get("label", "")
                        if ":" in market_name:
                            market_name = market_name.split(":")[1]
                        if "+" in market_name:
                            market_name = market_name.split("+")[1]
                        for outcome in offer.get("outcomes", []):
                            if "hidden" in outcome:
                                continue
                            odds_american = outcome.get("oddsAmerican")
                            odds_decimal = outcome.get("oddsDecimal")
                            team = outcome.get("label")
                            line = outcome.get("line")
                            if team == "No Goalscorer":
                                continue
                            if line is not None:
                                line = str(line)
                            
                            participant = outcome.get("participant")
                            sort_order = outcome.get("sortOrder")

                            if team in market_name:
                                market_name = market_name.replace(team, "")

                            if 'participants' in outcome:
                                participants = outcome["participants"][0]
                                if participants["name"] != "":
                                    participant = participants["name"]
                                participantType = participants["type"]
                            if participant == "":
                                    participant = outcome.get("label")
                            if participantType == "Team":
                                if team == team_1:
                                    alliases_team_1.add(format_string(participant))
                                if team == team_2:
                                    alliases_team_2.add(format_string(participant))
                            if team in participant:
                                participant = team

                            if not sort_order or team == participant:
                                if team_1 in market_name:
                                    market_name = market_name.replace(team_1, "")
                                    team = team_1
                                elif team_2 in market_name:
                                    market_name = market_name.replace(team_2, "")
                                    team = team_2
                                if  line and team in line:
                                    line = line.replace(team, "")
                                market_name = market_name.lstrip()
                                market_id = "^".join(map(format_string, filter(None, [market_name, team, line])))
                            else:
                                if participant in market_name:
                                    market_name = market_name.replace(participant, "")
                                if line and participant in line:
                                    line = line.replace(participant, "")
                                if  line and team in line:
                                    line = line.replace(team, "")
                                if team_1 in market_name:
                                    market_name = market_name.replace(team_1, "")
                                    participant = team_1
                                elif team_2 in market_name:
                                    market_name = market_name.replace(team_2, "")
                                    participant = team_2
                                market_name = market_name.lstrip()

                                market_id = "^".join(map(format_string ,filter(None, [market_name, participant, team, line])))

                            odds.append( {
                                "odds_american": odds_american,
                                "odds_decimal": odds_decimal,
                                "market_id": market_id,
                                "participant" : format_string(participant),
                                "participantType" : participantType
                            })

        for odd in odds:
            for allias in alliases_team_1:
                if allias in odd["market_id"]:
                    odd["market_id"] = odd["market_id"].replace(allias, format_string(team_1))
            for allias in alliases_team_2: 
                 if allias in odd["market_id"]:
                    odd["market_id"] = odd["market_id"].replace(allias, format_string(team_2))

        yield {
            "game_id": game_id,
            "odds" : odds
        } 

       


def format_string(input_string):
    formatted_string = input_string.replace(" ", "_").lower()
    return formatted_string

def create_game_id(game, league, team_1, team_2, date):
    components = [game, format_string(league), format_string(team_1), format_string(team_2), date]
    return "^".join(components)

