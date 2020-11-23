import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_data(pageNo):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
#     url = 'https://tiki.vn/dien-thoai-smartphone/c1795?src=c.1789.hamburger_menu_fly_out_banner&page='
    url = 'https://tiki.vn/bo-chia-mang-switch/c4454?page='
    
    r = requests.get(url + str(pageNo), headers=headers)
    # r.text is a HTML file so we will use html.parser
    soup = BeautifulSoup(r.text, 'html.parser')
    # Make the soup object look nicer
    
    
    ### We want to save information about all articles in a list
    data = []

    # Find all article tags
    products = soup.find_all('a', {'class':'product-item'})

    # Extract information of each article
    for product in products:

             # Each article is dictionary containing the required information:
        d = {'product_title':'', 'price':'', 'url_img': '', 'url_page':'' ,
                'tiki_now':'', 'free_ship':'', 'reviews':'', 'rating':'', 'under_price':'', 'discount':'', 'shocking_price':'',
                 'installment':'', 'free_gift':''}

            # We use the try-except blocks to handle errors
        try:
            d['product_title'] = product.find('div', {'class':'name'}).span.text
            d['price'] = product.find('div',{'class':'price-discount__price'}).text
            d['url_img'] = product.img['src']
            d['url_page'] = product['href']
            d['discount'] = product.find('div',{'class':'price-discount__discount'}).text

            # Review & rating   
            d['reviews'] = product.find('div',{'class':'review'}).text
            star = product.find('div',{'class':'rating'})
            d['rating'] = star.find_all('div')[1]['style']

            # Tikinow
            d['tiki_now'] = 1 if bool(product.find('div',{'class':'badge-service'}).div) else 0

            # Badge_under_price     
            d['under_price'] = 1 if bool(product.find('div',{'class':'badge-under-price'}).div) else 0

            # Free gift
            d['free_gift'] = 1 if bool(product.find('div',{'class':'freegift-list'})) else 0

            # paid_by_installment      
            d['installment'] = 1 if bool(product.find('div',{'class':'badge-benefits'}).span) else 0

            # Freeship / shocking price
            badge_top = product.find('div', {'class': 'badge-top'}).span.text if bool(product.find('div', {'class': 'badge-top'}).span) else 'NA'
            d['shocking_price'] = badge_top if badge_top != 'Freeship' else 'NA' 
            d['free_ship'] = badge_top if badge_top != 'Freeship' else 'NA'

                # Append the dictionary to data list
            data.append(d)

        except:
                # Skip if error and print error message
            print("We got one article error!")
            
    return data
            

pageNo = 1
result = get_data(pageNo) 
result
df = pd.DataFrame(data = result, columns = result[0].keys())
df['price'] = df['price'].str.replace(' ₫', '').str.replace('.', '').astype(int)
df['reviews'] = df['reviews'].str.replace('(','').str.replace(')','')
df['rating'] = df['rating'].str.replace('width:', '')
df