import requests
import pandas as pd
import pyshorteners

from bs4 import BeautifulSoup


def get_single_data_source(keyword):
    url = f"https://www.ebay.com/sch/i.html?_nkw={keyword}"
    html_page = requests.get(url).text
    soup = BeautifulSoup(html_page, 'lxml')
    return soup


def get_multi_data_source(keyword, page=1):
    url = f"https://www.ebay.com/sch/i.html?_nkw={keyword}&_pgn={page}"
    html_page = requests.get(url).text
    soup = BeautifulSoup(html_page, 'lxml')
    return soup

def get_next_page():
    # https://www.ebay.com/sch/i.html?_from=R40&_sacat=0&_nkw=playstation+5&_pgn=13&rt=nc
    '''
        ol pagination__items
        li pagination__item
        a['href']
    '''
    pass


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


def pd_write_csv(product_list):
    df = pd.DataFrame(product_list)
    df.to_csv('output.csv', index=False)
    print("Saved to CSV")

if  __name__ == '__main__':
    keyword = 'play+stattion+5'
    page = 20

    soup = get_single_data_source(keyword)
    product_list = extract_data(soup)
    pd_write_csv(product_list)
