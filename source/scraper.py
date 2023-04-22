import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import shutil

import json
from datetime import date


def get_pictures(url_list: list, search_key: str, height: int, width: int, quality: int, product_id: str,
                 folder_path: str, headers: str) -> None:
    """
    For a given list of pictures urls, detects the ones containing a search keyword and
    downloads all the pictures in the given resolution and quality. Saves them in a folder
    named after the product id
    :param
    url_list: the list with all the picture links
    search_key: the keyword to validate the link
    height: the height of the picture in pixels
    width: the width of the picture in pixels
    quality: the quality of the picture from 1 to 100
    product_id: the id of the product, comes from the url of the same product
    folder_path: the path where to save the pictures
    headers: headers for the requests()
    :return
    None
    """

    # Creates a base url with the given parameters, the url is not complete, it is missing the img id
    base_url = "https://cdn.deporvillage.com/cdn-cgi/image/h=" + str(height) + ",w=" + str(width) + ",f=auto,q=" + str(
        quality) + ",fit=contain,background=white/product/"

    absolute_path = os.path.dirname(__file__)
    path = os.path.join(absolute_path, folder_path, product_id)
    # Checks whether the folder exists or not, if it exists it doesn't download the pictures
    # The folder name is the product id
    if not os.path.exists(path):
        os.makedirs(path)
        for pic in url_list:
            # It only uses the pictures with the keyword in the address
            if search_key in pic:
                # The product code is the image name cleaned of the parameters and the rest of the url
                product_code = pic.split("/")[-1]
                # Creates a new URL with the new parameters and product code
                download_url = base_url + product_code
                print("Download url: ", download_url)
                r = requests.get(download_url, stream=True, headers=headers)
                img_path = os.path.join(path, product_code)
                print("status: ", r.status_code)
                if r.status_code == 200:
                    with open(img_path, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
        return


def get_product(address: str, head: str) -> tuple[str, dict]:
    """
    For a given url the function scrapes the page downloading all the significant information
    it also downloads the pictures and saves them in a folder.
    :param
    address: the web page address for the scraping
    headers: valid headers for the webpage

    :return
    product_id: the id of the product, it comes from the url, it's unique
    product: a dictionary with all the scraped information
    """

    html = requests.get(address, headers=head).content
    soup = BeautifulSoup(html, "lxml")

    product_id = address.split("/")[-1]

    # Gets the product name which is the page address and will be the key in the dictionary
    # product_name = soup.find("h1", {"itemprop": "name"}).get_text()
    try:
        product_name = soup.find("h1", {"class": "Product_product-title__Fbfnp"}).get_text()
        product_name = bytes(product_name, 'utf-8').decode('utf-8', 'ignore')
    except AttributeError:
        return None, None

    # Gets original price and retail price with the discount, getting the discount is not important
    try:
        original_price = soup.find("div", {"class": "Product_product-pvpr__RZCNy"}).get_text()
        original_price = bytes(original_price, 'utf-8').decode('utf-8', 'ignore')
    except AttributeError:
        original_price = None
    try:
        retail_price = soup.find("div", {"class": "Product_product-price__5keIc"}).get_text()
        retail_price = bytes(retail_price, 'utf-8').decode('utf-8', 'ignore')
    except AttributeError:
        retail_price = None

    # Gets the brand
    try:
        brand = soup.find("a", {"class": "Product_product-brand__TXJJO"}).get('title')
        brand = bytes(brand, 'utf-8').decode('utf-8', 'ignore')
    except AttributeError:
        brand = None

    product = {
        "Nombre Producto": product_name,
        "Precio Original": original_price,
        "Precio Venta": retail_price,
        "Marca": brand
    }

    # Gets the breadcrumb for the product
    breadcrumb = []
    try:
        breadcrumb_div = soup.findAll("li", {"class": "Breadcrumb_breadcrumb-item__U1xED"})
        for crumb in breadcrumb_div:
            breadcrumb.append(crumb.text.strip())
        product["Breadcrumb"] = breadcrumb
    except AttributeError:
        pass

    # Get the product tags
    product_tags = []
    try:
        product_tags_div = soup.find("div", {"class": "TagList_tag-list-component__E_c5m"})
        for tag in product_tags_div:
            product_tags.append(tag.text.strip())
        product["Tags"] = product_tags
    except AttributeError:
        pass

    try:
        stars_div = soup.find('div', {"class": "Stars_stars-component__eGPjV Stars_small__He_tJ"})
        stars_count = stars_div.findAll("span", {"class": "Stars_active__S3Jgc"})
        product["Estrellas"] = len(stars_count)
    except AttributeError:
        product["Estrellas"] = 0

    # Gets the description which contains most of the technical information
    try:
        description = soup.find("div", {"class": "ReadMore_read-more-content-wrapper__INEKb"}).get_text()

        desc_position = 0
        write_next: bool = False
        new_key = ""

        for line in description.splitlines():
            if desc_position == 0:
                # print(line)
                desc_position += 1
                product["Descripción"] = line
            else:
                if line:
                    # print(line)
                    if write_next:
                        product[new_key] = line
                        # print(line)
                        write_next = False
                    last_char = line[-1]
                    if last_char == ':':
                        new_key = line
                        write_next = True
    except AttributeError:
        pass

    # Uses selenium to get picture addresses, some img addresses are not available through BS scraping
    # Not even selecting all the 'img' elements
    # It opens the page and gets all the pictures from the page, then closes the page

    img_list = []
    driver = webdriver.Firefox()
    driver.get(address)
    for image in driver.find_elements(By.TAG_NAME, 'img'):
        img_list.append(image.get_attribute("src"))
    driver.close()

    for img in img_list:
        print(img)
    get_pictures(img_list, "product", 500, 500, 100, product_id, "img", head)

    product["datetime"] = str(datetime.now())

    return product_id, product


"""
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
}

page_url = "https://www.deporvillage.com/bicicleta-electrica-whistle-b-race-a8-1"
name, product_dict = get_product(page_url, headers)
print(name)
print(product_dict)
scraped_products = {name: product_dict}
filename = "deporvillage_bicicletas_" + str(date.today()) + ".json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(scraped_products, f, ensure_ascii=False)
"""