# import MPLogger
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from ProductData import ProductData
from datetime import datetime
from pprint import pprint
import time
from  collections import namedtuple
import sys,os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


PriceRecord = namedtuple('PriceRecord',['page','vendor_index','vendor', 'price',  'condition', 'delivery','shipping','cart_button'])

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
	'next_button_disabled': 'li.a-disabled.a-last',
	'current_page': 'la.a-selected',
	'add_to_cart' : ''
}
class AmazonRunner:

	def __init__(self,_webdriver ,_url , _manager_params, _browser_params):
		self.webdriver = _webdriver
		self.manager_params = _manager_params
		self.browser_params = _browser_params
		self.product_data = {}
		self.product_data['url'] = _url
		self.parsed_rows = []
		self.isMobile = False if self.browser_params['ua'] == "Mac" else True
		# self.webdriver.implicitly_wait(20)
		self.current_index = 0

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
		# if  len(self.webdriver.find_elements(By.CSS_SELECTOR,"li#olpTabNew")) > 0:
		# 		self.webdriver.find_element(By.CSS_SELECTOR,"li#olpTabNew").click()
		# 		time.sleep(2)
		self.product_data['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		while not self.webdriver.find_elements(By.CSS_SELECTOR,selectors['next_button_disabled']):
			try:
				page = self.webdriver.find_element(By.CSS_SELECTOR,'li.a-selected').text
				print 'current page: ',page
				self.parsed_rows += self.get_offer_details(page)
				self.webdriver.find_element(By.CSS_SELECTOR,selectors['next_button']).click()
				time.sleep(4)
			except Exception, e:
				print  e

		page = self.webdriver.find_element(By.CSS_SELECTOR,'li.a-selected').text
		self.parsed_rows += self.get_offer_details(page)
		return self.parsed_rows
		# self.product_data['prices'] = self.parsed_rows
		# print 'Items that need to be tested for checkout:'
		# # self.get_items_for_checkout()

	
	# def get_all_offers_new(self):
	# 	#TODO: Figure out what this if is for
	# 	if  len(self.webdriver.find_elements(By.CSS_SELECTOR,"li#olpTabNew")) > 0:
	# 			self.webdriver.find_element(By.CSS_SELECTOR,"li#olpTabNew").click()
	# 			time.sleep(2)
	# 	self.product_data['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	# 	while not self.webdriver.find_elements(By.CSS_SELECTOR,selectors['next_button_disabled']):
	# 		try:
	# 			self.parsed_rows += self.get_offer_details()

	def get_items_for_checkout(self):
		checkout_rows = []
		pprint(self.product_data['prices'])
		for p in self.product_data['prices']:
			if 'free shipping on eligible orders' in p.shipping.lower():
				print p
			# else:
			#  print p.vendor.lower()
		checkout_rows += filter(lambda x: 'amazon' in x.vendor.lower(), self.product_data['prices'])
		checkout_rows += filter(lambda x: 'amazon' in x.delivery.lower(), self.product_data['prices'])
		
	def get_offer_details(self,page):
		try:
			prices =  self.get_price()
			conditions = self.get_condition()
			deliveries = self.get_delivery()
			vendors = self.get_vendors()
			shipping = self.get_shipping()
			index,buttons = self.get_buttons()

			pd = []
			for i in xrange(len(prices)):
				p = PriceRecord(page,index[i],vendors[i],prices[i],conditions[i],deliveries[i],shipping[i],buttons[i])
				pd.append(p)
			return pd
		except Exception, e:
			print 'got an exception!'
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			print e

	def get_products_for_check_out(self,pd):
		it = []
		for p in pd:
			if 'free shipping on eligible orders' in p.shipping.lower():
				it.append(p)
		return it

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
	def get_buttons(self):
		buttons = []
		for el in self.webdriver.find_elements(By.CSS_SELECTOR,"form.a-spacing-none"):
			button = el.find_elements(By.CSS_SELECTOR,'[name="submit.addToCart"]')[0]
			el_index  = el.get_attribute('action').split('_')[-1]
			buttons.append((el_index,button))
		return  zip(*buttons)



	def get_add_to_cart(self):
		try:
				el = self.webdriver.find_elements(By.CSS_SELECTOR,"form.a-spacing-none")[0]
				#this gets the index from the post url. Most consistent way I can think of for keeping track of the index
				# self.webdriver.implicitly_wait(20)

				el_index = el.get_attribute('action')[-1]
				print 'element index :',el_index
				button = el.find_elements(By.CSS_SELECTOR,'[name="submit.addToCart"]')[0]
				button.click()

				cart = self.webdriver.find_element(By.CSS_SELECTOR,'a#hlb-ptc-btn-native')
				cart.click()

				self.re_sign_in()
				
				ship_to = self.webdriver.find_elements(By.CSS_SELECTOR,'a.a-declarative.a-button-text ')[0]
				ship_to.click()
				print 'ship to'
				# shipping_continue = self.webdriver.find_elements(By.CSS_SELECTOR,'[value="Continue"]')[0]
				# shipping_continue.click()
				
				wait = WebDriverWait(self.webdriver, 20)
				element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[value="Continue"]')))
				element.click()
				
				print 'shipping continue'
				
				# if not  self.webdriver.find_elements(By.CSS_SELECTOR,'input.a-button-input.a-button-text'):
				# 	print 'no elements'
				# 	self.webdriver.save_screenshot('test.png') 	
				# 	continue
				# card_continue = self.webdriver.find_elements(By.CSS_SELECTOR,'input.a-button-input.a-button-text')[0]
				# card_continue.click()	
				wait = WebDriverWait(self.webdriver, 20)
				element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'input.a-button-input.a-button-text')))
				element.click()
				print 'card continue'


				table_div = self.webdriver.find_element(By.CSS_SELECTOR,'div#subtotals-marketplace-table')
				table = table_div.find_elements(By.CSS_SELECTOR,'table')

				for row in table:
					for r in row.find_elements_by_tag_name("td"):
						print r.text

				# a[href="https://www.amazon.com/ref=ox_spc_footer_homepage"]
				homepage = self.webdriver.find_elements(By.CSS_SELECTOR,'#footer > div.a-color-secondary.a-size-mini > p > a:nth-child(4)')[0]
				
				print 'going to homepage page'
				
				homepage.click()
				
				time.sleep(4)
				# self.webdriver.save_screenshot('test.png')
				# #nav-flyout-ewc > div.nav-flyout-head.nav-tools.nav-sprite > a > span.nav-cart-icon.nav-sprite
				cart = self.webdriver.find_elements(By.CSS_SELECTOR,'span.nav-cart-icon.nav-sprite')[0]
				cart.click()
				time.sleep(4)
				self.webdriver.save_screenshot('test1.png')
				print 'should be at delete page'
				
				delete = self.webdriver.find_elements(By.CSS_SELECTOR,'input[value="Delete"]')[0]
				print'attribute',self.webdriver.find_elements(By.CSS_SELECTOR,'input[value="Delete"]')[0].get_attribute('aria-label')

				wait = WebDriverWait(self.webdriver, 20)
				element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'input[value="Delete"]')))
				
				element.click()

				# time.sleep(15)
				self.webdriver.save_screenshot('test3.png')
				webdriver.get(self.product_data['url'])
				self.get_offer_details()
				
				# break
		except Exception, e:
			print 'got an exception!'
			exc_type, exc_obj, exc_tb = sys.exc_info()
			if exc_tb:
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)
				print e

			
		print 'Done moving on'	
			# self.webdriver.save_screenshot('test.png') 
			# self.webdriver.find_element(By.CSS_SELECTOR,'#nav-cart-count').click()
			

	def get_vendors(self):
		v = []
		for i, el in enumerate(self.webdriver.find_elements(By.CSS_SELECTOR,selectors['vendor_name'])):
			count = i + 1
			if el.text:
				v.append(el.text)
			else:
				v.append(el.find_element_by_tag_name('img').get_attribute('alt'))
		return v

	def re_sign_in(self):
	    user = self.browser_params["creds_user"]
	    password = self.browser_params["creds_password"]
	    email = self.webdriver.find_element(By.CSS_SELECTOR, "input#ap_email").send_keys(user)
	    password = self.webdriver.find_element(By.CSS_SELECTOR, "input#ap_password").send_keys(password)
	    self.webdriver.find_element_by_id("signInSubmit").click()
	    print ("Signed in with %s"%user)