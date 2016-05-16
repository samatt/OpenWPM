from automation import TaskManager
import time
import os
from pprint import pprint 
import json

# The list of sites that we wish to crawl
files = os.listdir(os.path.join(os.path.dirname(__file__) ,'browser_settings'))
NUM_BROWSERS = 0

# for f in files:
# 	if '.DS_Store' not in f:
# 		NUM_BROWSERS =  NUM_BROWSERS + 1

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
DB_DIR = os.path.join(REPO, 'db')
# db_loc = DB_DIR + "/amazon-crawler.sqlite"

product_urls = TaskManager.load_product_urls()
manager_params, browser_params =TaskManager.load_amazon_params()

# for i in xrange(NUM_BROWSERS):
#     browser_params[i]['disable_flash'] = True
for i in xrange(NUM_BROWSERS):
    browser_params[i]['disable_flash'] = True

#debug
# browser_params  = [browser_params[0]]
# manager = TaskManager.TaskManager(DB_DIR, browser_params, 1)

manager = TaskManager.TaskManager(manager_params, browser_params, NUM_BROWSERS)

manager.sign_in()
manager.delete_cart()
# for cat,urls in product_urls.iteritems():
	# for url in urls:
		# manager.get_prices(url,cat)
		# time.sleep(2)
		
		# fp = open(os.path.join(os.path.dirname(__file__), 'price_index.json'))
		# for_check_out = json.load(fp)
		# for i in for_check_out['items']:
		# 	if not i['scraped']:
		# 		print 'getting prices for : ', i
		# 		manager.get_checkout_price(url,i)

# Shuts down the browsers and waits for the data to finish logging
manager.close()
