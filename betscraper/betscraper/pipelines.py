# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
from itemadapter import ItemAdapter


class BetscraperPipeline:
    def process_item(self, item, spider):
        
        adapter = ItemAdapter(item)

        date_str = adapter.get("date")
        if date_str == "Tomorrow":
            today = datetime.date.today()
            tomorrow = today + datetime.timedelta(days=1)
            adapter["date"] =  tomorrow.strftime("%d{th} %b").upper().replace("{TH}", get_ordinal(today.day))
        if date_str == "Today":
            today = datetime.date.today()
            adapter["date"] =  today.strftime("%d{th} %b").upper().replace("{TH}", get_ordinal(today.day))
        return item
    
def get_ordinal(n):
    return "th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
