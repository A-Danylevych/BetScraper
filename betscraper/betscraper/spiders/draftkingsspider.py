import scrapy

from betscraper.items import BetscraperItem


class DraftkingsspiderSpider(scrapy.Spider):
    name = "draftkingsspider"
    allowed_domains = ["sportsbook.draftkings.com"]
    start_urls = ["https://sportsbook.draftkings.com/sports/soccer"]
    base_url = "https://sportsbook.draftkings.com"

    def parse(self, response):
        leagues = response.css("a.league-link__link")

        for league in leagues:
            league_url = self.base_url + league.css("::attr(href)").get()
            yield response.follow(league_url, callback=self.parse_league)

    def parse_league(self, response):
        matches = response.css("a.sportsbook-event-accordion__title")

        for match in matches:
            match_url = self.base_url + match.css("::attr(href)").get()
            yield response.follow(match_url, callback=self.parse_match)

    def parse_match(self, response):
        event_league = response.css('nav.sportsbook-breadcrumb ol li:nth-last-child(2) a::text').get()
        match_name = response.css('nav.sportsbook-breadcrumb ol li:last-child h1::text').get()

        date_elements = response.css("span.sportsbook-event-accordion__date span::text").getall()
        date, time = self.parse_date_elements(date_elements)

        ul_element = response.css("ul.game-props-card17")[0]
        li_elements = ul_element.css("li.game-props-card17__cell")

        team_1, team_1_odd = self.extract_team_info(li_elements[0])
        team_2, team_2_odd = self.extract_team_info(li_elements[2])
        draw_odd = li_elements[1].css("span.sportsbook-odds.american.default-color::text").get()
        
        bet_item = BetscraperItem()
        bet_item["event_league"] = event_league
        bet_item["match_name"] = match_name
        bet_item["date"] = date
        bet_item["time"] = time
        bet_item["team_1"] = team_1
        bet_item["team_1_odd"] = team_1_odd
        bet_item["team_2"] = team_2
        bet_item["team_2_odd"] = team_2_odd
        bet_item["draw_odd"] = draw_odd

        yield bet_item

    def parse_date_elements(self, date_elements):
        if not date_elements:
            date = "Today"
            time = time.strftime("%I:%M %p")
        elif date_elements[1] == ' ':
            date = date_elements[0]
            time = date_elements[2]
        else:
            date_parts = date_elements[0].split()
            time = date_parts[-1]
            date = " ".join(date_parts[1:3])

        return date, time

    def extract_team_info(self, li_element):
        team = li_element.css("span.sportsbook-outcome-cell__label::text").get()
        odds = li_element.css("span.sportsbook-odds.american.default-color::text").get()
        return team, odds