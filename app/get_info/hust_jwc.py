import requests
from bs4 import BeautifulSoup
import chardet


class jwc_xinxi():
	def __init__(self,web_addr,title,time):
		self.web_addr=web_addr
		self.title=title
		self.time=time
	def show(self):
		pass
		'''print(self.web_addr)
		print(self.title)
		print(self.time)'''
##################返回教务要闻和教务通知共同组成的对象列表#########
def get_jwc():
	target_1='http://jwc.hust.edu.cn/syxw/jwyw.htm'		#教务要闻
	target_2='http://jwc.hust.edu.cn/syxw/jwtz.htm'		#教务通知
	addr='http://jwc.hust.edu.cn/'
	info=[]
	############获取教务要闻#######一页#########
	html=requests.get(url=target_1)
	text=html.text.encode(html.encoding).decode('utf-8')
	bf=BeautifulSoup(text,features='lxml')
	table33=bf.find_all('table',attrs={"id": "table33"})[1]
	tr=table33.find_all('tr')
	for tr_item in tr:
		a=tr_item.find('a')
		td=tr_item.find_all('td')[-1]
		info.append(jwc_xinxi(web_addr=addr+a['href'][2:],title=a['title'],time=td.get_text()))
		info[-1].show()
	############获取教务通知#####一页###########
	html=requests.get(url=target_2)
	text=html.text.encode(html.encoding).decode('utf-8')
	bf=BeautifulSoup(text,features='lxml')
	table33=bf.find_all('table',attrs={"id": "table33"})[1]
	tr=table33.find_all('tr')
	for tr_item in tr:
		a=tr_item.find('a')
		td=tr_item.find_all('td')[-1]
		info.append(jwc_xinxi(web_addr=addr+a['href'][2:],title=a['title'],time=td.get_text()))
		info[-1].show()
	return info

