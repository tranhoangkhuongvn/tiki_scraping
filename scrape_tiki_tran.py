#get data
import requests
from bs4 import BeautifulSoup


def get_url(url):
  #Tiki forbidden case, use headers
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
  r = requests.get('https://tiki.vn/', headers=headers)
  soup = BeautifulSoup(r.text, 'html.parser') 
  return soup


def scrape_tiki(url='https://tiki.vn/%27):
  soup = get_url(url)
  products = soup.find_all('product', {'class':'product-item'})
  print(products)
  data = []


#extract information

for product in products:

  p={'Product ID':'', 'Product Title' ='','Product URL' ='','Image URL' ='','Price' ='','Discount' ='','Tiki Now' ='','Free Delivery' ='','Total Reviews' ='','Rating Percentage' ='','Underprice Badge' ='','Shocking Price' ='','Paid Installment' ='','Free gift' =''}

  try:
    p['Product ID']= product.p['Product ID']
    p['Product Title']= product.p['Product Title']
    p['Product URL']= product.p['Product URL']
    p['Image URL']= product.p['Image URL']
    p['Price']= product.p['Price']
    p['Discount']= product.p['Discount']
    p['Tiki Now']= product.p['Tiki Now']
    p['Free Delivery']= product.p['Free Delivery']
    p['Total Reviews']= product.p['Total Reviews']
    p['Rating Percentage']= product.p['Rating Percentage']
    p['Underprice Badge']= product.p['Underprice Badge']
    p['Shocking Price']= product.p['Shocking Price']
    p['Paid Installment']= product.p['Paid Installment']
    p['Free Gift']= product.p['Free Gift']
    data.append(p)

return data

#data frame
products = pd.DataFrame(data = data, columns = data[0].keys())
products


#store data
products.to_csv("./result.csv", index=False)
