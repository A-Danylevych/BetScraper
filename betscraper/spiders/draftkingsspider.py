import json
import scrapy

from betscraper.items import BetscraperItem


class DraftkingsspiderSpider(scrapy.Spider):
    name = "draftkingsspider"
    allowed_domains = ["sportsbook.draftkings.com"]
    start_urls = ["https://sportsbook.draftkings.com/sports/soccer"]
    base_url = "https://sportsbook.draftkings.com"
    api_url = "https://sportsbook.draftkings.com/sites/US-SB/api/v3/event/"

    def parse(self, response):
        leagues = response.css("a.league-link__link")

        for league in leagues:
            league_url = self.base_url + league.css("::attr(href)").get()
            yield response.follow(league_url, callback=self.parse_league)

    def parse_league(self, response):
        matches = response.css("a.sportsbook-event-accordion__title")

        for match in matches:
            match_id = match.css("::attr(href)").get().split("/")[-1]
            yield response.follow(self.api_url + match_id + "?format=json", callback=self.parse_match)

    def parse_match(self, response):
        json_content = response.body.decode('utf-8')
        json_data = json.loads(json_content)
        game_data = json_data["event"]

        league = game_data["eventGroupName"]
        team_1 = game_data["teamName1"]
        team_2 = game_data["teamName2"]
        date = game_data["startDate"]

        game_id = "soccer:" + format_string(league) + ":" + format_string(team_1) + "^" + format_string(team_2) + "@" + date

        categories = json_data["eventCategories"][1:]

        for category in categories:
            for market in category["componentizedOffers"]:
                for offers in market["offers"]:
                    for offer in offers:
                        market_name = offer["label"]
                        for outcome in offer["outcomes"]:
                            if "hidden" in outcome:
                                continue
                            odds_american = outcome["oddsAmerican"]
                            odds_decimal = outcome["oddsDecimal"]
                            team = outcome["label"]
                            if "line" in outcome:
                                line =  ":" + str(outcome["line"])
                            else:
                                line = ""
                            
                            market_id = format_string(market_name) + ":" + format_string(team) + format_string(line)

                            yield {
                                "game_id" : game_id,
                                "odds_american" : odds_american,
                                "odds_decimal" : odds_decimal,
                                "market_id" : market_id
                            }

    
def format_string(input_string):
    formatted_string = input_string.replace(" ", "_").lower()
    return formatted_string