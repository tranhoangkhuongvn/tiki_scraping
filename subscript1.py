
import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3
import numpy as np
import re
from time import sleep
from random import randint

#declare global variables
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

product_id_ls = []
product_title_ls = []
price_ls = []
discount_ls = []
image_url_ls = []
product_url_ls = []
tikinow_ls = []
free_delivery_ls = []
num_reviews_ls = []
percentage_ratings_ls = []
badge_under_price_ls = []
discount_percent_ls = []
shocking_price_ls = []
paid_installment_ls = []
free_gift_ls = []
regex = re.compile('-p\d*\.')

# important urls 
tiki_now_img_url = 'https://salt.tikicdn.com/ts/upload/9f/32/dd/8a8d39d4453399569dfb3e80fe01de75.png'
under_price_url = 'https://salt.tikicdn.com/ts/upload/51/ac/cc/528e80fe3f464f910174e2fdf8887b6f.png'
badge_benefit_url = 'https://salt.tikicdn.com/ts/upload/ba/4e/6e/26e9f2487e9f49b7dcf4043960e687dd.png'


def get_tiki_data(url):
	failed_count = 0
	while True:
		try:
			r = requests.get(url, headers=headers)
		except:
			return None
		# r.text is a HTML file so we will use html.parser
		soup = BeautifulSoup(r.text, 'html.parser')
		# All occurences of the products in that page
		print("\nAll occurences of the product div sections:")
		products = soup.find_all('a', {'class':'product-item'})

		print("Number of products:", len(products))
		if (len(products) == 0):
			# some time it just does not work on 1st try	
			if (failed_count > 20):
				break
			failed_count += 1
			sleep(randint(8,15))	
		else:
			return products			
	
	return None


def scrape_data(product_list):
	for product in product_list:
		# print(product.prettify())
		try:
			product_link = product['href']
			product_url = 'http://tiki.vn' + product_link
			product_id = regex.findall(product_link)[0][1:-1] #somethinginere-p234234.html
			
			product_url_ls.append(product_url)
		except:
			print('product link got error. move on to next product')
			continue
			
		# grab image url
		try:
			image_url = product.img['src']
			
		except:
			image_url = "NA"
			
		image_url_ls.append(image_url)
		
		product_id_ls.append(product_id)
		
		# find name
		try:
			product_name = product.find('div', {'class':'name'}).span.text
		except:
			product_name = "NA"
		
		product_title_ls.append(product_name)
		
		# find price
		try:
			product_price = product.find('div', {'class': 'price-discount__price'}).text
			discount_pct = product.find('div', {'class': 'price-discount__discount'}).text
		except:
			product_price = "NA"
			discount_pct = "NA"
			
		discount_ls.append(discount_pct)
		price_ls.append(product_price)
		
		# Shocking price - FreeShip
		shock_price = None
		freeship = None
		
		try:
			addon = product.find('div', {'class': 'item top'})
			if addon.text == 'Freeship':
				freeship = 1
				shock_price = 0
			else:
				freeship = 0
				shock_price = 1
		except:
			# print('cant find div item top')
			shock_price = "NA"
			freeship = "NA"
		
		shocking_price_ls.append(shock_price)
		free_delivery_ls.append(freeship)
		
		# Extract review information
		num_review = None
		rating_pct = None
		try:
			review_rating = product.find('div', {'class': 'rating-review'})
			rating_pct = review_rating.find('div', {'class': 'rating__average'})['style'][6:]
			#print(rating_pct)
			num_review = product.find('div', {'class': 'review'}).text[1:-1]
			#print(num_review)
		except:
			num_review = "NA"
			rating_pct = "NA"
		
		num_reviews_ls.append(num_review)
		percentage_ratings_ls.append(rating_pct)
		
		
		# check TikiNow
		tikinow = 0
		try:
			badge_service = product.find('div', {'class': 'badge-service'})
			if badge_service.img['src'] == tiki_now_img_url:
				tikinow = 1
		except:
			tikinow = "NA"
		
		tikinow_ls.append(tikinow)
		
		# check under price
		under_price = 0
		try:
			under_price_badge = product.find('div', {'class': 'badge-under-price'})
			if under_price_badge.img['src'] == under_price_url:
				#print('Got underprice!')
				under_price = 1
		except:
			under_price = "NA"
			
		badge_under_price_ls.append(under_price)
		
		# check paid by installments:
		installment = 0
		try:
			badge_benefit = product.find('div', {'class': 'badge-benefits'})
			if badge_benefit.img['src'] == badge_benefit_url:
				#print('Tra gop!')
				installment = 1
		except:
			installment = 0
		
		paid_installment_ls.append(installment)
		
		# free gifts
		try:
			free_gift = product.find('div', {'class': 'freegift-list'}).span.text
			
		except:
			free_gift = "NA"
			
		free_gift_ls.append(free_gift)


if __name__ == '__main__':
	data = pd.DataFrame({
			'Product id': product_id_ls,
			'Product title': product_title_ls,
			'Product URL': product_url_ls,
			'Image URL': image_url_ls,
			'Price': price_ls,
			'Discount': discount_ls,
			'Tiki Now': tikinow_ls,
			'Free Delivery': free_delivery_ls,
			'Total reviews': num_reviews_ls,
			'Rating %': percentage_ratings_ls,
			'Under price badge': badge_under_price_ls,
			'Shocking price': shocking_price_ls,
			'Paid installments': paid_installment_ls,
			'Free Gifts': free_gift_ls
		})
	# create data frame out of individual lists as columns
	#tiki_webpage = 'https://tiki.vn/laptop-may-vi-tinh-linh-kien/c1846?page='
	# read out the data_subcat and numpy list
	data_subcat = pd.read_csv('data_subcat.csv')
	print(data_subcat.head(10))
	id_list = np.load('list1.npy')
	for each_id in id_list:
		#extract url:
		page_url = data_subcat.loc[each_id, ]['url']
		print(page_url)
		print('Scaping page:', page_url)
		for page_num in range(2):
			sleep(randint(1,4))
			soup = get_tiki_data(page_url) 
			if soup == None:
				print('Done web scraping')
				break
			scrape_data(soup)	
		

		data.to_csv('Tiki_week2.csv', mode='a', header=False)

	print('Done tiki web scraping!')




