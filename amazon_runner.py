from automation import TaskManager
import time
import os
from pprint import pprint 
import json
import time
# The list of sites that we wish to crawl
# files = os.listdir(os.path.join(os.path.dirname(__file__) ,'browser_settings'))
# NUM_BROWSERS = 0

# for f in files:
# 	if '.DS_Store' not in f:
# 		NUM_BROWSERS =  NUM_BROWSERS + 1

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
DB_DIR = os.path.join(REPO, 'db')
# db_loc = DB_DIR + "/amazon-crawler.sqlite"

product_urls = TaskManager.load_products()
# print product_urls
manager_params, browser_params =TaskManager.load_amazon_params()

# for i in xrange(NUM_BROWSERS):
#     browser_params[i]['disable_flash'] = True
# for i in xrange(NUM_BROWSERS):
    # browser_params[i]['disable_flash'] = True

#debug
# browser_params  = [browser_params[0]]
# manager = TaskManager.TaskManager(DB_DIR, browser_params, 1)
# manager_params['data_directory'] = '~/OpenWPM/'
manager = TaskManager.TaskManager(manager_params, browser_params,True)


manager.sign_in()

#GET PRICES FROM VENDORS LIST
for name,url,data in product_urls:
	if not data['has_vendors_list']:
		print 'adding ',name,' to queue for vendors list'
		print name
		manager.get_prices(url,name)
		time.sleep(2)

	# if 
	# 


# GET PRICES THAT REQUIRE CHECKOUT
for name,url,data in product_urls:	
	# for url in urls:
	fp = open(os.path.join(os.path.dirname(__file__), './product-prices/{}.json'.format(name)))	
	for_check_out = json.load(fp)

	for i in for_check_out['items']:
		if not i['scraped']:
			print 'adding  : ', i,' to queue'
			manager.delete_cart(name)
			manager.get_checkout_price(name,url,i)
			time.sleep(2)
		else:
			pass
			# print 'skipping ', i['vendor_index'],' as its already scraped'
# # Shuts down the browsers and waits for the data to finish logging
manager.close()
