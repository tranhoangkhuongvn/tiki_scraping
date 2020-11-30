#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import requests
import sqlite3
import pandas as pd

TIKI_URL = 'https://tiki.vn'


# In[2]:


PATH_TO_DB = '.'

conn = sqlite3.connect(PATH_TO_DB+'tiki.db')
cur = conn.cursor()


# In[3]:


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}


# In[4]:


# Get the HTML content get_url()
def get_url(url):
    try:
        response = requests.get(url,headers = HEADERS).text
        soup = BeautifulSoup(response, 'html.parser')
        return soup
    except Exception as err:
        print('ERROR BY REQUEST:', err)
        return None


# In[5]:


get_url(TIKI_URL).prettify()[0:500]


# #### Create Read Update Delete
# On database

# In[6]:


# Create table categories in the database using a function
def create_categories_table():
    query = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255),
            url TEXT, 
            parent_id INTEGER, 
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    try:
        cur.execute(query)
        conn.commit()
    except Exception as err:
        print('ERROR BY CREATE TABLE', err)
        
create_categories_table()


# In[7]:


# Insert a row of data to the table categories
query = """
    INSERT INTO categories (name, url, parent_id)
    VALUES (?, ?, ?);
"""

val = ('Phone','phone.xyz', 5)
try:
    cur.execute(query, val)
    cat_id = cur.lastrowid
    print(cat_id)
    conn.commit()

except Exception as err:
    print('ERROR BY INSERT:', err)


# In[8]:


query = """
    SELECT * 
    FROM categories
"""

for row in cur.execute(query):
    print(row)
conn.commit()


# In[9]:


cur.execute('SELECT * FROM categories;').fetchall()


# In[10]:


# Remove a row by using its id
query="""
    DELETE FROM categories WHERE id=?;
"""

val = (1,)

try:
    cur.execute(query, val)
    conn.commit()

except Exception as err:
    print('ERROR BY INSERT:', err)

cur.execute('SELECT * FROM categories;').fetchall()


# In[11]:


# drop the whole table to clean things up
cur.execute('DROP TABLE categories;')
conn.commit()

# recreate the table
create_categories_table()


# In[12]:


# Instead of using a function to do CRUD on database,
# creating a class Category is preferred
# attributes: name, url, parent_id
# instance method: save_into_db()
class Category:
    def __init__(self, name, url, parent_id=None, cat_id=None):
        self.cat_id = cat_id
        self.name = name
        self.url = url
        self.parent_id = parent_id

    def __repr__(self):
        return f"ID: {self.cat_id}, Name: {self.name}, URL: {self.url}, Parent: {self.parent_id}"

    def save_into_db(self):
        query = """
            INSERT INTO categories (name, url, parent_id)
            VALUES (?, ?, ?);
        """
        val = (self.name, self.url, self.parent_id)
        try:
            cur.execute(query, val)
            self.cat_id = cur.lastrowid
            conn.commit()
        except Exception as err:
            print('ERROR BY INSERT:', err)


# In[13]:


cat1 = Category('Phone-Tablet', 'https://tiki.vn/dien-thoai-may-tinh-bang/c1789')
cat1.save_into_db()
print(cat1.cat_id)


# In[14]:


cur.execute('SELECT * FROM categories;').fetchall()


# In[15]:


# display the category object
print(cat1)


# In[16]:


# prepare our categories table again
cur.execute('DROP TABLE categories;')
conn.commit()
create_categories_table()


# In[17]:


CATEGORY_SET = set()
def can_add_to_cat_set(cat_name,save=False):
    if cat_name not in CATEGORY_SET:
        if save:
            CATEGORY_SET.add(cat_name)
            print(f'Added "{cat_name}" to CATEGORY_SET')
        return True
    return False


# In[18]:


def get_main_categories(save_db=False):
    soup = get_url(TIKI_URL)

    result = []
    for a in soup.find_all('a', {'class': 'menu-link'}):
        name = a.find('span', {'class': 'text'}).text.strip()

        _ = can_add_to_cat_set(name,save_db)

        url = a['href']
        main_cat = Category(name, url) # object from class Category

        if save_db:
            main_cat.save_into_db()
        result.append(main_cat)
    
    return result




main_categories = get_main_categories(save_db=True)



# cur.execute('SELECT * FROM categories;').fetchall()




import re

# get_sub_categories() given a parent category
def get_sub_categories(parent_category, save_db=False):
    parent_url = parent_category.url
    #print(parent_url)
    result = []

    try:
        soup = get_url(parent_url)

        for a in soup.find_all('a', {'class':'item item--category'}):
            name = a.text.strip()
            if can_add_to_cat_set(name,save_db): 
                sub_url = a['href']
                cat = Category(name, sub_url, parent_category.cat_id) # we now have parent_id, which is cat_id of parent category
                if save_db:
                    cat.save_into_db()
                result.append(cat)
    
    except Exception as err:
        print('ERROR IN GETTING SUB CATEGORIES:', err)
    
    return result





from time import sleep
from random import randint


def get_all_categories(categories,save_db):
    # if I reach the last possible category, I need to stop
    if len(categories) == 0:
        return      
    for cat in categories:
        #print(f'Getting {cat} sub-categories...')
        sub_categories = get_sub_categories(cat, save_db=save_db)
        sleep(randint(1,3))
        #print(f'Finished! {cat.name} has {len(sub_categories)} sub-categories')
        get_all_categories(sub_categories,save_db=save_db) # make sure to switch on (or off) save_db here
    
    print('Done')




# drop the whole table to clean things up
cur.execute('DROP TABLE categories;')
conn.commit()

# re-create our category table again
create_categories_table()



get_all_categories(main_categories,save_db=True)






