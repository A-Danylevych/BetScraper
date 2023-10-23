import json
from flask import Flask, request, jsonify
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process

app = Flask(__name__)


def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl('draftkingsspider')
    process.start()


@app.route('/run-spider', methods=['GET'])
def start_spider():
    spider_process = Process(target=run_spider)
    spider_process.start()
    spider_process.join()
    return jsonify({'message': 'Spider is running'})


@app.route('/get-scraped-data', methods=['GET'])
def get_scraped_data():
    try:
        with open('betdata.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'Scraped data not found'})


if __name__ == '__main__':
    app.run()
