from automation import TaskManager
from automation import AmazonRunner
import time
import os
from pprint import pprint 


# files = os.listdir(os.path.join(os.path.dirname(__file__) ,'browser_settings'))


# REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
# DB_DIR = os.path.join(REPO, 'db')

NUM_BROWSERS = 0
product_urls = TaskManager.load_product_urls()
manager_params, browser_params =TaskManager.load_amazon_params()
# amazon = AmazonRunner(webdriver, url, manager_params, browser_params )

for i in xrange(NUM_BROWSERS):
    browser_params[i]['disable_flash'] = True

manager = TaskManager.TaskManager(manager_params, browser_params, NUM_BROWSERS)
manager.sign_in()

# for cat,urls in product_urls.iteritems():
# 	for url in urls:
# 		manager.get_prices(url,cat)
# 		time.sleep(2)

# Shuts down the browsers and waits for the data to finish logging
manager.close()
