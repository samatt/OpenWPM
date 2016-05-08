# import MPLogger
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from ProductData import ProductData
from datetime import datetime
import time
from  collections import namedtuple
import os

PriceRecord = namedtuple('PriceRecord',['vendor','vendor_index', 'price',  'condition', 'delivery','shipping'])

selectors = {
	'title': '[data-feature-name="title"]',
	'new_offers_link_desktop':'span.olp-padding-right > a',
	'new_offers_link_mobile':'div#olp > a',
	'prices' : 'span.a-size-large.a-color-price.olpOfferPrice',
	'condition': 'span.a-size-medium.olpCondition.a-text-bold',
	'delivery': 'div.a-column.a-span3.olpDeliveryColumn',
	'shipping': 'p.olpShippingInfo',
	'vendor_name':'h3.a-spacing-none.olpSellerName',
	'next_button': 'li.a-last',
	'next_button_disabled': 'li.a-disabled.a-last'
}
class AmazonRunner:

	def __init__(self,_webdriver ,_url , _manager_params, _browser_params):
		self.webdriver = _webdriver
		self.manager_params = _manager_params
		self.browser_params = _browser_params
		self.product_data = {}
		self.product_data['url'] = _url
		self.parsed_rows = []
		# print "Here",_url
		# self.product_data = ProductData(_url)
		# self.product_data.url = _url
		# print dir(self.product_data)
		# self.product_data['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.isMobile = False if self.browser_params['ua'] == "Mac" else True

	def get_els(self,selector,fn=None):
		try:
			if fn:
				return filter(fn, self.webdriver.find_elements(By.CSS_SELECTOR,selector))
			else:
				return self.webdriver.find_elements(By.CSS_SELECTOR,selector)
		except Exception, e:
			print 'error in get els', e
			return []


	def get_product_name(self):
		self.product_data['name'] = self.webdriver.find_element(By.CSS_SELECTOR,selectors['title']).text

	def nav_to_offers(self):
		if self.isMobile:
			els = self.get_els(selectors['new_offers_link_mobile'], lambda x: 'new' or 'New' in x.text)
		else:
			els = self.get_els( selectors['new_offers_link_desktop'],lambda x: "new" in x.text)
		if els:
			els[0].click()
			return True
		else:
			print "Cant find element"
			return False

	def get_all_offers(self):
		#TODO: Figure out what this if is for
		
		if  len(self.webdriver.find_elements(By.CSS_SELECTOR,"li#olpTabNew")) > 0:
				self.webdriver.find_element(By.CSS_SELECTOR,"li#olpTabNew").click()
				time.sleep(2)
		self.product_data['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		while not self.webdriver.find_elements(By.CSS_SELECTOR,selectors['next_button_disabled']):
			try:
				self.parsed_rows += self.get_offer_details()
				self.webdriver.find_element(By.CSS_SELECTOR,selectors['next_button']).click()
			except Exception, e:
				print  e
			time.sleep(2)

		print 'Im here!'
		self.parsed_rows += self.get_offer_details()
		self.product_data['prices'] = self.parsed_rows

	def get_offer_details(self):
		prices =  self.get_price()
		conditions = self.get_condition()
		deliveries = self.get_delivery()
		vendors = self.get_vendors()
		shipping = self.get_shipping()
		
		pd = []
		for i in xrange(len(prices)):
			p = PriceRecord(vendors[i][0],vendors[i][1],prices[i],conditions[i],deliveries[i],shipping[i])
			pd.append(p)
		return pd

	def get_price(self):
		els = self.get_els(selectors['prices'])
		return [el.text for el in els]
	
	def get_condition(self):
		els = self.get_els(selectors['condition'])
		return [el.text for el in els]
	
	def get_delivery(self):
		els = self.get_els(selectors['delivery'])
		return [el.text.split('\n')[0] for el in els]

	def get_shipping(self):
		els = self.get_els(selectors['shipping'])
		return [el.text for el in els]
		    # product_data['shipping'] += [element.text for element in webdriver.find_elements(By.CSS_SELECTOR,"p.olpShippingInfo")]

	def get_vendors(self):
		v = []
		for i, el in enumerate(self.webdriver.find_elements(By.CSS_SELECTOR,selectors['vendor_name'])):
			count = i + 1
			if el.text:
				v.append((el.text,count))
			else:
				v.append((el.find_element_by_tag_name('img').get_attribute('alt'),count))
		return v
