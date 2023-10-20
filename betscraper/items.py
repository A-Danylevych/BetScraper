# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BetscraperItem(scrapy.Item):
    event_league = scrapy.Field()
    match_name = scrapy.Field()
    date = scrapy.Field()
    time = scrapy.Field()
    team_1 = scrapy.Field()
    team_1_odd = scrapy.Field()
    team_2_odd = scrapy.Field()
    team_2 = scrapy.Field()
    draw_odd = scrapy.Field()