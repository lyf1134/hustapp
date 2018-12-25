import requests
from bs4 import BeautifulSoup

class inter_xinxi():
	def __init__(self,web_addr,title,time):
		self.web_addr=web_addr
		self.title=title			#信息发布时间
		self.time=time
	def show(self):
		print(self.web_addr)
		print(self.title)
		print(self.time)

########返回一个对象列表##########		
def get_inter_xinxi():
	list_inter_xinxi=[]
	###########获取留学信息网本科留学信息，一页##########
	page='http://www.husthosts.com/index.php/liuxuexiangmu/benkeshengchuguo'
	html=requests.get(url=page)
	#print(html.text)
	bf=BeautifulSoup(html.text,features='lxml')
	main=bf.find('div',attrs={"class": "col-main right"})
	ul=main.find('ul')
	info=ul.find_all('div',attrs={"class": "box_title"})
	for info_item in info:
		span=info_item.find('span')				
		a=info_item.find('a')
		list_inter_xinxi.append(inter_xinxi(web_addr=a['href'],title=a.get_text(),time=span.get_text()))
	##########获取交换生项目信息，三页###############
	page_list=['http://www.husthosts.com/index.php/liuxuexiangmu/jiaohuanshengxiangmu',
	'http://www.husthosts.com/index.php/liuxuexiangmu/jiaohuanshengxiangmu/index-2.html',
	'http://www.husthosts.com/index.php/liuxuexiangmu/jiaohuanshengxiangmu/index-3.html']
	for page in page_list:
		html=requests.get(url=page)
		#print(html.text)
		bf=BeautifulSoup(html.text,features='lxml')
		main=bf.find('div',attrs={"class": "col-main right"})
		ul=main.find('ul')
		info=ul.find_all('div',attrs={"class": "box_title"})
		for info_item in info:
			span=info_item.find('span')				
			a=info_item.find('a')
			list_inter_xinxi.append(inter_xinxi(web_addr=a['href'],title=a.get_text(),time=span.get_text()))
	##########获取冬夏令营信息，三页#################
	page_list=['http://www.husthosts.com/index.php/liuxuexiangmu/dongxialingying',
	'http://www.husthosts.com/index.php/liuxuexiangmu/dongxialingying/index-2.html',
	'http://www.husthosts.com/index.php/liuxuexiangmu/dongxialingying/index-2.html']
	for page in page_list:
		html=requests.get(url=page)
		#print(html.text)
		bf=BeautifulSoup(html.text,features='lxml')
		main=bf.find('div',attrs={"class": "col-main right"})
		ul=main.find('ul')
		info=ul.find_all('div',attrs={"class": "box_title"})
		for info_item in info:
			span=info_item.find('span')				
			a=info_item.find('a')
			list_inter_xinxi.append(inter_xinxi(web_addr=a['href'],title=a.get_text(),time=span.get_text()))
	#########获取寒暑期课程项目，两页###################
	page_list=['http://www.husthosts.com/index.php/liuxuexiangmu/hanshuqikechengxiangmu',
	'http://www.husthosts.com/index.php/liuxuexiangmu/hanshuqikechengxiangmu/index-2.html']
	for page in page_list:
		html=requests.get(url=page)
		#print(html.text)
		bf=BeautifulSoup(html.text,features='lxml')
		main=bf.find('div',attrs={"class": "col-main right"})
		ul=main.find('ul')
		info=ul.find_all('div',attrs={"class": "box_title"})
		for info_item in info:
			span=info_item.find('span')				
			a=info_item.find('a')
			list_inter_xinxi.append(inter_xinxi(web_addr=a['href'],title=a.get_text(),time=span.get_text()))
	###########获取港澳台项目，一页####################
	page='http://www.husthosts.com/index.php/liuxuexiangmu/gangaotaidiquxiangmu'
	html=requests.get(url=page)
	#print(html.text)
	bf=BeautifulSoup(html.text,features='lxml')
	main=bf.find('div',attrs={"class": "col-main right"})
	ul=main.find('ul')
	info=ul.find_all('div',attrs={"class": "box_title"})
	for info_item in info:
		span=info_item.find('span')				
		a=info_item.find('a')
		list_inter_xinxi.append(inter_xinxi(web_addr=a['href'],title=a.get_text(),time=span.get_text()))
	return list_inter_xinxi
