import requests
import pandas as pd
import pyshorteners

from flask import Flask, make_response
from flask_restful import Resource, Api
from bs4 import BeautifulSoup

def get_data_source(keyword, pages):
    url = f"https://www.ebay.com/sch/i.html?_nkw={keyword}&_pgn={pages}"
    html_page = requests.get(url).text
    soup = BeautifulSoup(html_page, 'lxml')
    return soup

def extract_data(soup):
    product_list = list()
    results = soup.findAll('div', class_='s-item__info clearfix')[1:]

    def extract_sold(item):
        return item.find('span', class_ = 's-item__dynamic s-item__quantitySold') and item.find('span', class_ = 's-item__dynamic s-item__quantitySold').span.text.replace('sold','').replace(',', '').strip() or None
    
    def extract_watchers(item):
        return item.find('span', class_ = 's-item__dynamic s-item__watchCountTotal') and item.find('span', class_ = 's-item__dynamic s-item__watchCountTotal').span.text.replace('watchers','').replace('+', '').strip() or None
    
    def url_shorter(long_url):
        type_tiny = pyshorteners.Shortener()
        short_url = type_tiny.tinyurl.short(long_url)
        return short_url

    for item in results:
        product = dict()
        product["title"] = item.find('div', class_ = 's-item__title').span.text
        product["sold_price"] = item.find('span', class_ = 's-item__price').text.replace('VND', '').replace(',', '').strip()
        product["watcher"] = extract_watchers(item)
        product["sold"] =  extract_sold(item)
        product["link"] = url_shorter(item.find('a', class_ ='s-item__link')['href'])
        product_list.append(product)

    return product_list
    
def pd_write_csv(product_list, page):
    df = pd.DataFrame(product_list)
    df.to_csv(f'output-{page}.csv', index=False)
    print("Saved to CSV")

# Config Apps
app = Flask(__name__)
api = Api(app)

class ProductListing(Resource):
    def get(self, keyword=None, pages=1):
        print("Request for product listing with keyword: " + keyword)
        products_list = list()
        for page in range(1, pages + 1):
            multi_soup = get_data_source(keyword,page)
            products_list.append(extract_data(multi_soup))
        
        return {'ProductListing': products_list, 'Amount': len(products_list)}
        
api.add_resource(ProductListing, '/', '/<string:keyword>/<int:pages>')


class Export2Csv(Resource):
    def get(self, keyword=None, pages=1):
        multi_soup = get_data_source(keyword,pages)
        df = pd.DataFrame(extract_data(multi_soup))
        response  = make_response(df.to_csv(index=False))
        response.headers["Content-Disposition"] = "attachment; filename=export.csv"
        response.headers["Content-Type"] = "text/csv"
        return response

api.add_resource(Export2Csv, '/', '/csv/<string:keyword>/<int:pages>')

if  __name__ == '__main__':
    print("Starting the product listing API")
    app.run(debug=True)
