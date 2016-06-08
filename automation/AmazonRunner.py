# import MPLogger
import sys,os,json,time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from ProductData import ProductData
from datetime import datetime
from pprint import pprint
from  collections import namedtuple
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import time

PriceRecord = namedtuple('PriceRecord',['page','vendor_index','vendor', 'price',  'condition', 'delivery','shipping','tax','scraped'])

selectors = {
	'title': '[data-feature-name="title"]',
	'new_offers_link_desktop':'span.olp-padding-right > a',
	'new_offers_link_mobile':'div#olp > a',
	'prices' : 'span.a-size-large.a-color-price.olpOfferPrice',
	'condition': 'span.a-size-medium.olpCondition.a-text-bold',
	'delivery': 'div.a-column.a-span3.olpDeliveryColumn',
	'shipping': 'p.olpShippingInfo',
	'tax':'span.olpEstimatedTaxText',
	'vendor_name':'h3.a-spacing-none.olpSellerName',
	'next_button': 'li.a-last',
	'next_button_disabled': 'li.a-disabled.a-last',
	'current_page': 'la.a-selected',
	'add_to_cart' : '[name="submit.addToCart"]',
	'proceed_to_checkout':'a#hlb-ptc-btn-native',
	'pop-over':'h4#a-popover-header-2',
	'pop-over-2':'h4#a-popover-header-3',
	'no-thanks':'button#siNoCoverage-announce',
	'shipping_continue':'a.a-declarative.a-button-text',
}
class AmazonRunner:

	def __init__(self,_webdriver ,_name,_url , _manager_params, _browser_params):
		self.webdriver = _webdriver
		self.name = _name
		# self.product_fp = os.path.join(os.path.dirname(__file__), '../products-url/{}.json'.format(_name))
		self.prices_fp = os.path.join(os.path.dirname(__file__), '../product-prices/{}.json'.format(_name))
		print "product-prices json url",self.prices_fp
		self.manager_params = _manager_params
		self.browser_params = _browser_params
		self.screenshot_path = os.path.join(os.path.dirname(__file__),'../product-screenshots')
		self.product_data = {}
		self.product_data['url'] = _url
		self.product_data['time'] = datetime.now().strftime("%Y-%m-%d")
		self.parsed_rows = []
		self.isMobile = False if self.browser_params['ua'] == "Mac" else True
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
		print 'nav to offers'
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
		self.product_data['time'] = datetime.now().strftime("%Y-%m-%d")
		if self.webdriver.find_elements(By.CSS_SELECTOR,'li.a-selected'):		
			while not self.webdriver.find_elements(By.CSS_SELECTOR,selectors['next_button_disabled']):
				try:
						page = self.webdriver.find_element(By.CSS_SELECTOR,'li.a-selected').text
						print 'current page: ',page
						# self.name
						#product-screenshots
						img = "{}/{}-{}-{}.png".format(self.screenshot_path,self.product_data['time'],self.name.replace(" ","_"),page)
						print 'saving to: ',img
						self.webdriver.save_screenshot(img)
						self.parsed_rows += self.get_offer_details(page)
						self.webdriver.find_element(By.CSS_SELECTOR,selectors['next_button']).click()
						time.sleep(2)
						print 'going to the next page'
				except Exception, e:
					print  e
					return self.parsed_rows

			if self.webdriver.find_element(By.CSS_SELECTOR,'li.a-selected'):
				print 'last page'
				page = self.webdriver.find_element(By.CSS_SELECTOR,'li.a-selected').text
				img = "{}/{}-{}-{}.png".format(self.screenshot_path,self.product_data['time'],self.name.replace(" ","_"),page)
				print 'saving to: ',img
				self.webdriver.save_screenshot(img)
				self.parsed_rows += self.get_offer_details(page)
		else:
			print 'looks like theres one page'
			self.parsed_rows += self.get_offer_details("1")
			img = "{}/{}-{}-{}.png".format(self.screenshot_path,self.product_data['time'],self.name.replace(" ","_"),"1")
			print 'saving to: ',img
			self.webdriver.save_screenshot(img)
			time.sleep(2)
		return self.parsed_rows

	def get_offer_details(self,page):
		try:
			prices =  self.get_price()
			conditions = self.get_condition()
			deliveries = self.get_delivery()
			vendors = self.get_vendors()
			shipping = self.get_shipping()
			# tax = self.get_tax()
			index,buttons = self.get_buttons()

			size = [len(index),len(vendors),len(prices),len(conditions),len(deliveries),len(shipping)]
			if len(set(size)) <= 1:
				pd = []
				for i in xrange(len(prices)):
					# if tax:
					# 	p = PriceRecord(page,index[i],vendors[i],prices[i],conditions[i],deliveries[i],shipping[i],None,False)
					# else:
					print (len(index),len(vendors),len(prices),len(conditions),len(deliveries),len(shipping),"$ 0",False)
					p = PriceRecord(page,index[i],vendors[i],prices[i],conditions[i],deliveries[i],shipping[i],None,False)
					pd.append(p)
				return pd
			else:
				print 'Missing some data so skipping this page'
				return [PriceRecord(page,"-1","missing","missing","missing","missing","missing",None,False)]
		except Exception, e:
			print 'got an exception!'
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			print e
			return [PriceRecord(page,"-1","missing","missing","missing","missing","missing",None,False)]

	def get_products_for_check_out(self,pd):
		it = []
		o = []
		print pd
		for p in pd:
			if 'missing' in p.shipping or 'exception' in p.shipping:
				i = {}
				i['page'] = p.page
				i['vendor_index'] = 'missing'
				i['vendor'] = 'missing'
				i['scraped'] = 'missing'
				i['for_checkout'] = False
				it.append(i)
			elif 'free shipping on eligible orders' in p.shipping.lower():
				i = {}
				i['page'] = p.page
				i['vendor_index'] = p.vendor_index
				i['vendor'] = p.vendor
				i['scraped'] = p.scraped
				i['for_checkout'] = True
				it.append(i)
			else:
				#TODO: Make one big list
				i = {}
				i['page'] = p.page
				i['vendor_index'] = p.vendor_index
				i['vendor'] = p.vendor
				i['scraped'] = True
				i['for_checkout'] = False
				# it.append(i)
				
				price = float(p.price.replace("$","").replace(",",""))
				
				if p.shipping and 'shipping' in p.shipping:
					print p.shipping
					shipping = float(p.shipping.split(' ')[1].replace("$","").replace(",",""))
					print shipping
				elif p.shipping and  'free' in p.shipping.lower():
					shipping = 0
				else:
					print 'weird shit with shipping skipping '
					continue

				if p.tax:
					tax = float(p.tax.split(' ')[1].replace("$",""))
				else:
					tax = 0
				before_tax = price + shipping
				total = before_tax + tax
				i['price_items'] = {'total':total,'before_tax':before_tax,'price':price,'shipping':shipping}
				it.append(i)

		with open(self.prices_fp, 'w') as fp:
			
			data = {'has_vendors_list':True,'url':self.product_data['url'],'items':it,'first_time':False}
			print 'saving data to file',self.prices_fp
			json.dump(data, fp,indent=2 )
		return o

	def get_price(self):
		els = self.get_els(selectors['prices'])
		return [el.text for el in els]
	
	def get_condition(self):
		els = self.get_els(selectors['condition'])
		return [el.text for el in els]
	
	def get_delivery(self):
		els = self.get_els(selectors['delivery'])
		return [el.text.split('\n')[0] for el in els]
	
	def get_tax(self):
		els = self.get_els(selectors['tax'])
		return [el.text for el in els]

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
		if buttons:
			return  zip(*buttons)
		else:
			return (None,None)


	def go_to_page(self,item):
		# not self.webdriver.find_elements(By.CSS_SELECTOR,selectors['next_button_disabled']):
		self.webdriver.save_screenshot('test.png') 	
		if self.webdriver.find_elements(By.CSS_SELECTOR,'li.a-selected'):
			while self.webdriver.find_element(By.CSS_SELECTOR,'li.a-selected').text.strip() != item['page']:
				try:
					page = self.webdriver.find_element(By.CSS_SELECTOR,'li.a-selected').text
					print 'current page: ',page
					self.webdriver.find_element(By.CSS_SELECTOR,selectors['next_button']).click()
					time.sleep(2)
					print 'going to the next page'
				except Exception, e:
					print  e

			print 'Done! At page: ',self.webdriver.find_element(By.CSS_SELECTOR,'li.a-selected').text
		else:
			print 'Only 1 pages'


	def get_shipping_cart(self,item):
		print 'in get shipping cart'
		data =False
		try:
			
			for el in self.webdriver.find_elements(By.CSS_SELECTOR,"form.a-spacing-none"):
				el_index = el.get_attribute('action').split('_')[-1]
				if self.webdriver.find_elements(By.CSS_SELECTOR,'li.a-selected'):
					cur_page = self.webdriver.find_element(By.CSS_SELECTOR,'li.a-selected').text
				else:
					cur_page = "1"
				
				print 'target: ',item['vendor_index'],item['page']
				print 'current: ',el_index,cur_page
				
				if item['vendor_index'] == el_index and item['page'] == cur_page:
					print 'correct vendor'
					print 'correct page'
					data = self.get_add_to_cart(el,item)
					break

			if data:
				print 'should have got price'
				data['vendor_index'] = item['vendor_index']
				return data
			else:
				print 'didnt get price'
				return False
			
		except Exception, e:
			print e
			return False


	def get_add_to_cart(self,el,item):
		data = {}
		print 'get_add_to_cart' 
		try:
				

				# self.webdriver.implicitly_wait(30)
				el_index = el.get_attribute('action')[-1]
				print 'element index :',el_index
				
 				# '[name="submit.addToCart"]'

				button = el.find_elements(By.CSS_SELECTOR,selectors['add_to_cart'])[0]
				button.click()
				
				time.sleep(2)	
				# 'a#hlb-ptc-btn-native'
				cart = self.webdriver.find_element(By.CSS_SELECTOR,selectors['proceed_to_checkout'])
				cart.click()
				
				time.sleep(4)	
				if self.webdriver.find_elements(By.CSS_SELECTOR,selectors['pop-over']):
					print 'has pop-over'
					self.webdriver.find_element(By.CSS_SELECTOR,selectors['no-thanks']).click()
					print 'clicked no thanks'
				elif self.webdriver.find_elements(By.CSS_SELECTOR,selectors['pop-over-2']):
					print 'has pop-over'
					self.webdriver.find_element(By.CSS_SELECTOR,selectors['no-thanks']).click()
					print 'clicked no thanks'
				time.sleep(2)
					# self.re_sign_in()
				self.re_sign_in()
				# self.webdriver.save_screenshot('test.png') 	
				
				#'a.a-declarative.a-button-text'
				
				ship_to = self.webdriver.find_elements(By.CSS_SELECTOR,selectors['shipping_continue'])[0]
				ship_to.click()
				print 'ship to'
				time.sleep(2)
				#TODO: Add the rest of the selectors to the dict
				shipping_continue = self.webdriver.find_elements(By.CSS_SELECTOR,'[value="Continue"]')[0]
				# self.webdriver.save_screenshot("{}{}".format(self.manager_params["screenshot-folder"],''))
				# print "{}/{}-{}.png".format(self.manager_params["screenshot-folder"],self.name,item['page'],item['vendor_index'])
				img = "{}/{}-{}-{}-{}.png".format(self.screenshot_path,self.product_data['time'],self.name.replace(" ","_"),item['page'],item['vendor_index'])
				time.sleep(2)
				shipping_continue.click()
				
				print 'shipping continue'

				
				# time.sleep(1)
				card_continue = self.webdriver.find_element(By.CSS_SELECTOR,'input#continue-top')
				card_continue.click()	
				print 'card continue'
				time.sleep(2)
				img = "{}/{}-{}-{}.png".format(self.screenshot_path,self.product_data['time'],self.name.replace(" ","_"),item['page'],item['vendor_index'])
				self.webdriver.save_screenshot(img) 	
				print 'saving screenshot to ',img
				table_div = self.webdriver.find_element(By.CSS_SELECTOR,'div#subtotals-marketplace-table')
				table = table_div.find_elements(By.CSS_SELECTOR,'table')
				price_data = [] 
				for row in table:
					for r in row.find_elements_by_tag_name("td"):
						price_data.append(r.text)
				print 'num items: ',len (price_data)
				# pprint(self.parse_check_out_price(price_data))
				data['prices'] = self.parse_check_out_price(price_data)
				return data
				# break
		except Exception, e:
			print 'got an exception!'
			self.webdriver.save_screenshot('error.png') 	
			exc_type, exc_obj, exc_tb = sys.exc_info()
			if exc_tb:
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)
				print e
				return False

		print 'Done moving on'	
	def parse_check_out_price(self,price_data):

		i_p,i_s,i_t = 1,3,8

		price = float(price_data[i_p].replace("$",""))
		shipping = float(price_data[i_s].replace("$",""))
		tax = float(price_data[i_t].replace("$",""))
		before_tax = price + shipping
		total = before_tax + tax
		return {'total':total,'before_tax':before_tax,'price':price,'shipping':shipping}

	def delete_cart(self):
		if int(self.webdriver.find_elements(By.CSS_SELECTOR,'span#nav-cart-count')[0].text) == 0:
			print 'no items in cart!'
		else:
			cart = self.webdriver.find_elements(By.CSS_SELECTOR,'span.nav-cart-icon.nav-sprite')[0]
			cart.click()
			time.sleep(2)
			print 'should be at delete page'
			
			for delete in self.webdriver.find_elements(By.CSS_SELECTOR,'input[value="Delete"]'):
				print'attribute',delete.get_attribute('aria-label')
				delete.click()
				time.sleep(2)

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
		if self.webdriver.find_elements(By.CSS_SELECTOR, "input#ap_email"):
		    user = self.browser_params["creds_user"]
		    password = self.browser_params["creds_password"]
		    email = self.webdriver.find_element(By.CSS_SELECTOR, "input#ap_email").send_keys(user)
		    password = self.webdriver.find_element(By.CSS_SELECTOR, "input#ap_password").send_keys(password)
		    self.webdriver.find_element_by_id("signInSubmit").click()
		    print ("Signed in with %s"%user)
		else:
			print 'no user form'