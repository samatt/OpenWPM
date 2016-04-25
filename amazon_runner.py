from automation import TaskManager
import time
import os
from pprint import pprint 


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

for cat,urls in product_urls.iteritems():
	for url in urls:
		manager.get_prices(url,cat)
		time.sleep(2)

# Shuts down the browsers and waits for the data to finish logging
manager.close()
