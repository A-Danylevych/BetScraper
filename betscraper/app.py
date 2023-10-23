import json
from flask import Flask, request, jsonify
from scrapy.crawler import CrawlerProcess
from betscraper.spiders.draftkingsspider import DraftkingsspiderSpider

app = Flask(__name__)

@app.route('/run-spider', methods=['GET'])
def run_spider():
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output.json', 
    })
    process.crawl(DraftkingsspiderSpider)
    process.start() 

    return jsonify({'message': 'Spider is running'})

@app.route('/get-scraped-data', methods=['GET'])
def get_scraped_data():
    try:
        with open('output.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'Scraped data not found'})
    
if __name__ == '__main__':
    app.run(debug=True)
