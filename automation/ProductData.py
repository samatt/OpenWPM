from datetime import datetime
from  collections import namedtuple

PriceRecord = namedtuple('PriceRecord',['vendor_index' ,'price', 'vendor', 'condition', 'delivery','shipping'])
class ProductData():
	def __init__(self,url):
		self.url =url
		# self._time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		# self._price = []
		# self._vendor = []
		# self._condition = []
		# self._delivery = []
		# self._vendor_index = []
		# self._shipping = []
		# self._num_items = 0

	# @property
	# def url(self):
	# 	return self._url
	
	# @url.setter
	# def url(self,value):
	# 	self._url = value
	# @url.getter
	# def url(self):
	# 	return self._url

	# @property
	# def time(self):
	# 	return self._time

	# @property
	# def price(self):
	# 	return self._price

	# @property
	# def vendor(self):
	# 	return self._vendor
	
	# @property
	# def condition(self):
	# 	return self._condition
	
	# @property
	# def vendor_index(self):
	# 	return self._vendor_index

	# @property
	# def shipping(self):
	# 	return self._shipping

	# @property
	# def num_items(self):
	# 	return self._num_items

	# def get_data_dump(self):
	# 	return [self.get_row(r) for i in xrange(self._num_items)]

	# def get_row(self,i):
	# 	return PriceRecord(self._vendor_index[i],self._prices[i],self._vendors[i],self._condition[i],self._delivery[i],self._shipping[i])
	# 	