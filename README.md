# Scrapy Web Scraping Project with Proxy Support
A web crawler in Python that scrapes football betting odds data from a bookmaker's website and saves this data. 

## Prerequisites

Before getting started, make sure you have the following prerequisites installed on your system:

- **Python**: Scrapy is a Python framework, so ensure that you have Python 3.x installed. You can download and install Python from [python.org](https://www.python.org/downloads).

- **Scrapy**: Scrapy is a powerful web scraping framework for Python. You can install it using pip:
    ```bash
    pip install scrapy
    ```

## Configuration
### Proxy Setup

To use a proxy for web scraping, follow these steps:

1. **Provide a Proxy List**: You should have a list of proxy IP addresses and ports in a text file. The default filename is `proxy_list.txt`. Each line in the file should contain one proxy in the format `http://ip:port`.

2. **Customize Proxy List File (Optional)**: If you wish to use a proxy list file with a different name, open the `settings.py` file in Scrapy project directory. Find the `PROXY_FILE_PATH` setting and specify the file path:

   ```python
   PROXY_FILE_PATH = 'proxy_list.txt'
   ```
The web scraping program is designed to use a proxy server rotation mechanism. When initiating a connection to a target website, the program will try to connect through a proxy server in a random order. If it fails to connect to the server, the program will continue execution without using this server.
### Configure Feeds (Output Formats) 

If you want to specify the output format for the scraped data and customize where it is saved, open the settings.py file. You can use the FEEDS setting to define the output formats and file paths:
   ```python
   FEEDS = {
    "betdata.csv" : { "format" : "csv", "overwrite" : True },
    "betdata.json" : { "format" : "json", "overwrite" : True }
    }
   ```
   Default configuration will save the data in both CSV and JSON formats with the specified file names.
## RUN
To start the web crawler, use the following command:
```bash
python -m scrapy crawl draftkingsspider
```