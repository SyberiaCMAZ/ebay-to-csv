
from bs4 import BeautifulSoup
import requests, lxml
from tqdm import tqdm
import pandas as pd
from datetime import datetime

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44"}


def get_product_name(ean): #implement rotating proxies
    response = requests.get(f"https://www.ean-search.org/?q={ean}",headers=headers)
    #Check for status
    response.raise_for_status()
    print(response)
    soup = BeautifulSoup(response.content, 'html.parser')
    product_name = soup.find('a',attrs= {'rel' : 'noopener noreferrer nofollow'})
    print(product_name)
    return product_name.get_text()


def get_ebay(ean):
    html = requests.get(f'https://www.ebay.com/sch/i.html?_nkw={ean}&_ipg=240', headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    today = datetime.today().strftime('%Y-%m-%d')
    data = []
    shippingEdit =''
    for i in tqdm(soup.select('.s-item__wrapper.clearfix'), desc='Processing'):
        
        title = i.select_one('.s-item__title').text
        link = i.select_one('.s-item__link')['href']
        
        try:
            condition = i.select_one('.SECONDARY_INFO').text
        except:
            condition = None

        try:
            shipping = i.select_one('.s-item__logisticsCost').text
        except:
            shipping = None
        if shipping != None:
            shippingEdit = shipping.replace('+','').replace(' shipping estimate', '').replace('shipping', '')

        try:
            location = i.select_one('.s-item__itemLocation').text.replace('from ', '')
        except:
            location = None

        if i.select_one('.s-item__etrs-badge-seller') is not None:
            top_rated = True
        else:
            top_rated = False

        try:
            bid_count = i.select_one('.s-item__bidCount').text
        except:
            bid_count = None


        if bid_count == None:
            bid = ''
        else:
            bid = True

        try:
            price = i.select_one('.s-item__price').text
        except:
            price = None

        data.append({
            'Title': title, 'Link': link, 
            'Price': price,
            'Condition': condition,
            'Trusted Seller': top_rated,
            'Shipping price': shippingEdit, 'Location': location,
            'Bid?': bid ,'count': bid_count
        })
    #print(data[1])
    #print(json.dumps(data, indent = 2, ensure_ascii = False))
    #print(len(data))
    df = pd.DataFrame.from_records(data)
    #print(df)
    df = df.iloc[1: , :]
    undrsc = ean.replace(' ','_')
    df.to_csv(f'ebay_raport_{undrsc}_{today}.csv')

def main():
    x = input('Enter EAN code or product name: ')
    #print(get_product_name(x))
    get_ebay(x)
    print("DONE!")


if __name__ == '__main__':
        main()
    
