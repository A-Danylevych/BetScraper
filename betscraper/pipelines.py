# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
from itemadapter import ItemAdapter
import pymongo
import sys

class MongoDBPipeline:

    collection = 'bets'

    def __init__(self, mongodb_uri, mongodb_db):
        self.mongodb_uri = mongodb_uri
        self.mongodb_db = mongodb_db
        if not self.mongodb_uri: sys.exit("You need to provide a Connection String.")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri=crawler.settings.get('MONGODB_URI'),
            mongodb_db=crawler.settings.get('MONGODB_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_db]
        self.db[self.collection].delete_many({})

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        adapter = dict(ItemAdapter(item))
        self.db[self.collection].insert_one(adapter)
        return item

class BetscraperPipeline:
    def __init__(self) -> None:
        #self.league_mapping = self.load_mapping('leagues.csv')
        #self.teams_mapping = self.load_mapping('teams.csv')
        #self.market_mapping = self.load_mapping('mapping.csv')
        pass

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        odds = adapter.get("odds")
        game, league, team_1, team_2, date = adapter.get("game_id").split("^")

        game_market = self.load(game+".csv")
        teams = self.load_team(game + "-teams.csv")   
        leagues = self.load(game + "-leagues.csv")
        labels = self.load_team(game+"-lables.csv")

        for odd in odds:
            market_id = odd.get("market_id")
            team_1_l = {"titles" : team_1,"league" : league }
            team_2_l = {"titles" : team_2,"league" : league }

            if not team_1_l in teams:
                teams.append(team_1_l)
            if not team_2_l in teams:
                teams.append(team_2_l)
            
            if not league in leagues:
                leagues.append(league)

            participantType = odd.get("participantType")
            participant = odd.get("participant")

            if participantType == "Player":
                if not participant == "":
                    market_id = market_id.replace(participant, "PLAYER_NAME")
                
                participant_l = {"titles" : participant,"league" : league }
                if not participant_l in labels:
                    labels.append(participant_l)
            
            if not team_1 =="" and team_1 in market_id:
                market_id = market_id.replace(team_1, "TEAM_1")
                                
            if not team_2 =="" and team_2 in market_id:
                market_id = market_id.replace(team_2, "TEAM_2")
                
            if not market_id in game_market:
                game_market.append(market_id)
        new_market = [] 
        for market_id in game_market:       
            for player in labels:
                if player["titles"] in market_id:
                    market_id = market_id.replace(player["titles"], "PLAYER_NAME")
            if not market_id in new_market:
                new_market.append(market_id)

        self.save_team(game +"-teams.csv", teams)
        self.save(game+"-leagues.csv", leagues)
        self.save_team(game+"-lables.csv", labels)     
        self.save(game+".csv", new_market)
        return item
    
    def load_mapping(self, csv_file):
        title_mapping = {}
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                reference_title = row['reference_title']
                current_title = row['current_title']
                title_mapping[current_title] = reference_title
        return title_mapping
    
    def load(self, csv_file):
        mapp = []
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                mapp.append(row['titles'])
        return mapp
    
    def save(self, csv_file, titles):
        with open(csv_file, 'w', newline='') as file:
            fieldnames = ['titles']  
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            writer.writeheader()

            for title in titles:
                writer.writerow({'titles': title})
    
    def load_team(self, csv_file):
        mapp = []
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                mapp.append({'titles': row['titles'], 'league': row['league']})
        return mapp

    def save_team(self, csv_file, data):
        with open(csv_file, 'w', newline='') as file:
            fieldnames = ['titles', 'league'] 
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()

            for entry in data:
                writer.writerow({'titles': entry['titles'], 'league': entry['league']})
    
