import requests
from bs4 import BeautifulSoup
from msql import mysql

class hust_news():
	def __init__(self,time,title,web_addr):
		self.time=time
		self.title=title
		self.web_addr=web_addr
	def show(self):
		print(self.time)
		print(self.title)
		print(self.web_addr)
		
def get_lectures():					##讲坛目录信息
	class_lectures=[]
	addr_1='http://news.hust.edu.cn/'
	html=requests.get(url='http://news.hust.edu.cn/162/list1.htm')
	bf=BeautifulSoup(html.text.encode(html.encoding).decode('utf-8'),features='lxml')
	ul=bf.find('ul',attrs={'class':'wp_article_list'})
	lectures=ul.find_all('li')
	for item in lectures:
		a=item.find('a')
		class_title=a.get_text()
		class_web_addr=addr_1+a['href']
		class_time='unknown'
		class_lectures.append(hust_news(time=class_time,title=class_title,web_addr=class_web_addr))
	#for item in class_lectures:
	#	item.show()
	return class_lectures

def get_important_news():			####学校要闻
	class_important_news=[]
	addr_1='http://news.hust.edu.cn/'
	target_list=['http://news.hust.edu.cn/155/list1.htm',
	'http://news.hust.edu.cn/155/list2.htm',
	'http://news.hust.edu.cn/155/list3.htm']
	for target in target_list:
		html=requests.get(url=target)
		bf=BeautifulSoup(html.text.encode(html.encoding).decode('utf-8'),features='lxml')
		ul=bf.find('ul',attrs={'class':'wp_article_list'})
		important_news=ul.find_all('li')
		for item in important_news:
			a=item.find('a')
			class_title=a.get_text()
			class_web_addr=addr_1+a['href']
			class_time='unknown'
			class_important_news.append(hust_news(time=class_time,title=class_title,web_addr=class_web_addr))
		#for item in class_important_news:
		#	item.show()
	return class_important_news

def get_hust_people():				##华中大人物
	class_hust_people=[]
	addr_1='http://news.hust.edu.cn/'
	html=requests.get(url='http://news.hust.edu.cn/161/list.htm')
	bf=BeautifulSoup(html.text.encode(html.encoding).decode('utf-8'),features='lxml')
	ul=bf.find('ul',attrs={'class':'wp_article_list'})
	hust_people=ul.find_all('li')
	for item in hust_people:
		a=item.find('a')
		class_title=a.get_text()
		class_web_addr=addr_1+a['href']
		class_time='unknown'
		class_hust_people.append(hust_news(time=class_time,title=class_title,web_addr=class_web_addr))
	#for item in class_hust_people:
	#	item.show()
	return class_hust_people

def get_hust_school():				##华中大校园
	class_hust_school=[]
	addr_1='http://news.hust.edu.cn/'
	html=requests.get(url='http://news.hust.edu.cn/159/list.htm')
	bf=BeautifulSoup(html.text.encode(html.encoding).decode('utf-8'),features='lxml')
	ul=bf.find('ul',attrs={'class':'wp_article_list'})
	hust_school=ul.find_all('li')
	for item in hust_school:
		a=item.find('a')
		class_title=a.get_text()
		class_web_addr=addr_1+a['href']
		class_time='unknown'
		class_hust_school.append(hust_news(time=class_time,title=class_title,web_addr=class_web_addr))
	#for item in class_hust_school:
	#	item.show()
	return class_hust_school


def get_news_text(id):		#返回mysql信息
	if id ==1:
		class_list=get_lectures()
	elif id ==2:
		class_list=get_important_news()
	elif id ==3:
		class_list=get_hust_people()
	elif id ==4:
		class_list=get_hust_school()
	mysql_list=[]
	for item in class_list: 
		try:
			class_title=item.title
		except:
			class_title=' '
		try:
			class_tim=item.date
		except:
			class_tim=' '
		try:
			class_place=item.host_addr
		except:
			class_place=' '
		try:
			class_url=item.web_addr
		except:
			class_url=' '
		class_content='['
		target=item.web_addr
		html=requests.get(url=target)
		bf=BeautifulSoup(html.text.encode(html.encoding).decode('utf-8'),features='lxml')
		###############获取文字信息##########
		read=bf.find("div",attrs={'class':'read'})
		p_list=read.find_all('p')
		text=''
		for item in p_list:
			if(item.find('br')!=None):
				continue
			text+=(item.get_text())
		class_content+=('{\"type\":\"text\",\"content\":\"'+text+'\"}')
		class_content+=']'
		################获取发表时间########
		time_text=bf.find('span',class_='arti_update')
		try:
			class_tim=time_text.text[5:]
		except:
			pass
		mysql_list.append(mysql( title=class_title,tim=class_tim, place=class_place,url=class_url,content=class_content))
	return mysql_list



