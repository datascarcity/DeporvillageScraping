"""
The main code for the web scraping
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from time import sleep
from scraper import get_product
import json
from datetime import date
import logging

if __name__ == '__main__':
    logging.basicConfig(filename="std.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Defines a global scope variable that contains the links to each product page
    products_to_scrape = list()
    # Define a header that works with this website
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
    }

    main_url = 'https://www.deporvillage.com'
    allowed_domains = ['deporvillage.com']


    class scrape_pages(scrapy.Spider):
        name = 'scrape_pages'

        def start_requests(self):
            # Defines an array with the categories to scrap and generates a URL for each one of them
            product_range = ['bicicletas']

            urls = [f'{main_url}/{product}' for product in product_range]

            # For each category parses the n pages looking for the products
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)

        def parse(self, response):
            print("Parsing: " + response.url)

            # Creates a scrapy selector with all the products div, this changes often and has to be updated
            # products = response.css('div.ProductList-module-list-item') previous selector
            products = response.css('div.ProductList_list-item__qqx2K')
            # print('Number of products per page:', len(products))

            # Loops through the selector to get the links for each one for later use and appends them to the array
            for product in products:
                product_link = product.css('a::attr(href)').get()
                products_to_scrape.append(product_link)
                print("Product link: ", product_link)

            # Navigates to the next page, if the page is not empty keeps going adding page numbers
            if(len(products)) != 0:
                print(response.url)
                # If it's the first page it goes to the second one using the numeration pattern
                if '?' not in response.url:
                    next_page_url = "?p=2"
                else:
                    # If it's past the second page it continues adding page numbers
                    current_page = int(response.url.partition('?p=')[2])
                    next_page_url = "?p="+str(current_page+1)

                next_url = response.urljoin(next_page_url)
                print("Next Url:", next_url)
                logger.info("Next Url:", next_url)

                if next_url is not None:
                    yield scrapy.Request(response.urljoin(next_url))

    # Creates a process with the crawler
    process = CrawlerProcess({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
    process.crawl(scrape_pages)
    process.start()

    # Creates a dictionary with the scraped data for each product, the dictionary will be dumped
    # into a json file
    scraped_products = {}

    # Loops through the products list to download the data for each page
    # Calls the scraper from scraper.py, url pattern is quite straightforward
    for product in products_to_scrape:
        page_url = f'{main_url}{product}'
        product_name, product_dict = get_product(page_url, headers)
        scraped_products[product_name] = product_dict
        logger.info("Product name:", product_name)
        sleep(0.2)

    # Writes the json file with the results
    filename = "deporvillage_bicicletas_"+str(date.today())+".json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(scraped_products, f, ensure_ascii=False)
