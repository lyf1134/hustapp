import requests
from bs4 import BeautifulSoup
	
########就业信息网函数库#########


########招聘会############
class zhaopinghui():
	def __init__(self,title,web_addr,date,host_addr):
		self.title=title			#公司名称
		self.web_addr=web_addr		#网络地址
		self.date=date				#举办日期
		self.host_addr=host_addr	#举办地点
	def show(self):
		print(self.title,
				self.web_addr,
				self.date,
				self.host_addr)
########函数解释###########
########自动获取招聘会目录上信息，并以列表形式返回########
def get_zhaopinghui_list():	
	#招聘会
	end_addr=''
	zhaopinghui_list=[]
	data=[]
	#组成目录页面
	target_1='http://job.hust.edu.cn/searchJob_'
	target_2='.jspx?type=0&fbsj=0'
	#首页
	first_page='http://job.hust.edu.cn/searchJob_1.jspx?type=0&fbsj=0'
	#拼装链接
	addr='http://job.hust.edu.cn/'	
	addr_1='http://job.hust.edu.cn'				
	html=requests.get(url=first_page)
	bf=BeautifulSoup(html.text,features='lxml')
	get=bf.find_all('a')
	#获取最后一页的链接地址
	for get_item in get:#########################没有末页##################################
		#print(get_item)
		if get_item.string=='末页':
			end_addr=addr+get_item['href']
			#print(addr+get_item['href'])
	#print(html.text)
	i=1
	while 1:
		target=target_1+str(i)+target_2
		#print(target)					每一分页面的链接
		html=requests.get(url=target)
		bf=BeautifulSoup(html.text,features='lxml')
		get=bf.find_all('table')
		'''for item in get:
			data.append(item.find_all('a'))'''
		tr=(get[1].find_all('tr'))
		tr=tr[1:]
		for tr_item in tr:
			td=tr_item.find_all('td')
			a=tr_item.find('a')
			class_web_addr=addr_1+a['href']			#原网页链接
			count=0
			class_date=td[1].find('span').string
			class_host_addr=td[2].find('span').string
			class_title=td[0].find('a').string
			zhaopinghui_list.append(zhaopinghui(web_addr=class_web_addr,date=class_date,host_addr=class_host_addr,title=class_title))
			#zhaopinghui_list[-1].show()
			#print('\n\n\n')
		i+=1
		if target==end_addr:									#跳出页面
			break
	return zhaopinghui_list

########医科招聘会
class yk_zhaopinhui():
	def __init__(self,title,web_addr,date,host_addr):
		self.title=title
		self.web_addr=web_addr
		self.date=date	
		self.host_addr=host_addr
	def show(self):
		print(self.title)
		print(self.web_addr)
		print(self.date)
		print(self.host_addr)
##########函数介绍###############
##########自动获取医科招聘会信息，并且返回一个list类型###医科招聘会信息只存储在一页上##		
def get_yk_zhaopinhui_list():
	#医科招聘会
	yk_zhaopinhui_list=[]
	information=[]
	data=[]
	#组成目录页面
	target_1='http://job.hust.edu.cn/searchJob_'
	target_2='.jspx?type=1&fbsj=0'
	#首页
	first_page='http://job.hust.edu.cn/searchJob_1.jspx?type=4&fbsj=3'
	#拼装链接
	addr='http://job.hust.edu.cn/'	
	addr_1='http://job.hust.edu.cn'				
	#print(html.text)
	i=1
	while 1:
		target=target_1+str(i)+target_2
		#print(target)										#每一分页面的链接
		html=requests.get(url=target)
		bf=BeautifulSoup(html.text,features='lxml')
		body=bf.find('div',class_='plate-body')
		table=body.find_all('table',class_='fdhy_tb002')
		'''for item in get:
			data.append(item.find_all('a'))'''
		#print(table[1])
		data=table[1].find_all('tr')
		data=data[1:]
		#print(data)
		for data_item in data:
			td=data_item.find_all('td')
			a=data_item.find_all('a')
			class_web_addr=addr_1+a[1]['href']			#原网页链接
			count=0
			class_title=td[0].get_text().strip()
			class_date=td[1].get_text().strip()
			class_host_addr=td[2].get_text().strip()			
			yk_zhaopinhui_list.append(yk_zhaopinhui(title=class_title,date=class_date,web_addr=class_web_addr,host_addr=class_host_addr))
			yk_zhaopinhui_list[-1].show()
		i=i+1
		if i==2:					        			#跳出页面
			break
	return yk_zhaopinhui_list
	

#####招聘信息
class zhaopinxinxi():
	def __init__(self,title,web_addr,date):
		self.title=title
		self.web_addr=web_addr
		self.date=date	
	def show(self):
		print(self.title)
		print(self.web_addr)
		print(self.date)	
###函数解释###########
###自动获取招聘信息目录网站的信息，并返回上述类别列表####只获取前10页信息####
def get_zhaopinxinxi_list():
	#招聘信息
	zhaopinxinxi_list=[]
	information=[]
	data=[]
	#组成目录页面
	target_1='http://job.hust.edu.cn/searchJob_'
	target_2='.jspx?type=2&fbsj=3'
	#首页
	first_page='http://job.hust.edu.cn/searchJob_1.jspx?type=2&fbsj=0'
	#拼装链接
	addr='http://job.hust.edu.cn/'	
	addr_1='http://job.hust.edu.cn'				
	#print(html.text)
	i=1
	while 1:
		target=target_1+str(i)+target_2
		#print(target)										#每一分页面的链接
		html=requests.get(url=target)
		bf=BeautifulSoup(html.text,features='lxml')
		body=bf.find('div',class_='plate-body')
		table=body.find_all('table',class_='fdhy_tb002')
		'''for item in get:
			data.append(item.find_all('a'))'''
		#print(table[1])
		data=table[1].find_all('tr')
		data=data[1:]
		#print(data)
		for data_item in data:
			td=data_item.find_all('td')
			a=data_item.find_all('a')
			class_web_addr=addr_1+a[1]['href']			#原网页链接
			count=0
			class_title=td[0].get_text().strip()
			class_date=td[1].get_text().strip()
			zhaopinxinxi_list.append(zhaopinxinxi(title=class_title,date=class_date,web_addr=class_web_addr))
			zhaopinxinxi_list[-1].show()
			#print('############')
		i=i+1
		if i>10:					        			#跳出页面
			break
	return zhaopinxinxi_list

#####医科招聘信息
class yk_zhaopinxinxi():
	def __init__(self,title,web_addr,date):
		self.title=title
		self.web_addr=web_addr
		self.date=date	
	def show(self):
		print(self.title)
		print(self.web_addr)
		print(self.date)
##########函数介绍###############
##########自动获取医科招聘信息，并且返回一个list类型###只获取前5页信息##		
def get_yk_zhaopinxinxi_list():
	#招聘信息
	yk_zhaopinxinxi_list=[]
	information=[]
	data=[]
	#组成目录页面
	target_1='http://job.hust.edu.cn/searchJob_'
	target_2='.jspx?type=3&fbsj=3'
	#首页
	first_page='http://job.hust.edu.cn/searchJob_1.jspx?type=4&fbsj=3'
	#拼装链接
	addr='http://job.hust.edu.cn/'	
	addr_1='http://job.hust.edu.cn'				
	#print(html.text)
	i=1
	while 1:
		target=target_1+str(i)+target_2
		#print(target)										#每一分页面的链接
		html=requests.get(url=target)
		bf=BeautifulSoup(html.text,features='lxml')
		body=bf.find('div',class_='plate-body')
		table=body.find_all('table',class_='fdhy_tb002')
		'''for item in get:
			data.append(item.find_all('a'))'''
		#print(table[1])
		data=table[1].find_all('tr')
		data=data[1:]
		#print(data)
		for data_item in data:
			td=data_item.find_all('td')
			a=data_item.find_all('a')
			class_web_addr=addr_1+a[1]['href']		#原网页链接
			count=0
			class_title=td[0].get_text().strip()
			class_date=td[1].get_text().strip()
			yk_zhaopinxinxi_list.append(yk_zhaopinxinxi(title=class_title,date=class_date,web_addr=class_web_addr))
			yk_zhaopinxinxi_list[-1].show()
		i=i+1
		if i==5:					        			#跳出页面
			break
	return yk_zhaopinxinxi_list

######实习生信息
class shixishengxinxi():
	def __init__(self,title,web_addr,date):
		self.title=title
		self.web_addr=web_addr
		self.date=date	
	def show(self):
		print(self.title)
		print(self.web_addr)
		print(self.date)
##########函数介绍###############
##########自动获取实习生信息，并且返回一个list类型###只获取前10页信息##	
def get_shixishengxinxi_list():
	#实习生信息
	shixishengxinxi_list=[]
	information=[]
	data=[]
	#组成目录页面
	target_1='http://job.hust.edu.cn/searchJob_'
	target_2='.jspx?type=4&fbsj=3'
	#首页
	first_page='http://job.hust.edu.cn/searchJob_1.jspx?type=4&fbsj=3'
	#拼装链接
	addr='http://job.hust.edu.cn/'	
	addr_1='http://job.hust.edu.cn'				
	#print(html.text)
	i=1
	while 1:
		target=target_1+str(i)+target_2
		#print(target)										#每一分页面的链接
		html=requests.get(url=target)
		bf=BeautifulSoup(html.text,features='lxml')
		body=bf.find('div',class_='plate-body')
		table=body.find_all('table',class_='fdhy_tb002')
		'''for item in get:
			data.append(item.find_all('a'))'''
		#print(table[1])
		data=table[1].find_all('tr')
		data=data[1:]
		#print(data)
		for data_item in data:
			td=data_item.find_all('td')
			a=data_item.find_all('a')
			class_web_addr=addr_1+a[1]['href']			#原网页链接
			count=0
			class_title=td[0].get_text().strip()
			class_date=td[1].get_text().strip()
			shixishengxinxi_list.append(shixishengxinxi(title=class_title,date=class_date,web_addr=class_web_addr))
			shixishengxinxi_list[-1].show()
		i=i+1
		if i>10:					        			#跳出页面
			break
	return shixishengxinxi_list

##########通知公告
class tongzhigonggao():
	def __init__(self,title,web_addr,date):
		self.title=title
		self.web_addr=web_addr
		self.date=date	
	def show(self):
		print(self.title)
		print(self.web_addr)
		print(self.date)
##########函数介绍###############
##########自动获取通知公告信息，并且返回一个list类型###获取前5页内容##		
def get_tongzhigonggao_list():
	#通知公告
	tongzhigonggao_list=[]
	information=[]
	data=[]
	#组成目录页面
	target_1='http://job.hust.edu.cn/notice/index_'
	target_2='.htm'
	#首页
	first_page='http://job.hust.edu.cn/notice/index_1.htm'
	#拼装链接
	addr='http://job.hust.edu.cn/'	
	addr_1='http://job.hust.edu.cn'				
	#print(html.text)
	i=1
	while 1:
		target=target_1+str(i)+target_2
		#print(target)										#每一分页面的链接
		html=requests.get(url=target)
		bf=BeautifulSoup(html.text,features='lxml')
		body=bf.find('ul',class_='info clearfix')
		li=body.find_all('li')
		#print(data)
		for li_item in li:
			a=li_item.find_all('a')
			span=li_item.find('span')
			if a[0]['href'][1]=='n':
				class_web_addr=addr_1+a[0]['href']			#原网页链接
			else :
				continue											#若不是校内网站，则跳过
			count=0
			class_title=a[0].get_text().strip()
			class_date=span.get_text().strip()
			tongzhigonggao_list.append(tongzhigonggao(title=class_title,date=class_date,web_addr=class_web_addr))
			tongzhigonggao_list[-1].show()
		i=i+1
		if i==5:					        			#跳出页面
			break
	return tongzhigonggao_list
	

######新闻动态
class xinwendongtai():
	def __init__(self,title,web_addr,date):
		self.title=title
		self.web_addr=web_addr
		self.date=date	
	def show(self):
		print(self.title)
		print(self.web_addr)
		print(self.date)
##########函数介绍###############
##########自动获取新闻动态信息，并且返回一个list类型###获取前5页内容##		
def get_xinwendongtai_list():
	#通知公告
	xinwendongtai_list=[]
	information=[]
	data=[]
	#组成目录页面
	target_1='http://job.hust.edu.cn/news/index_'
	target_2='.htm'
	#首页
	first_page='http://job.hust.edu.cn/notice/index_1.htm'
	#拼装链接
	addr='http://job.hust.edu.cn/'	
	addr_1='http://job.hust.edu.cn'				
	#print(html.text)
	i=1
	while 1:
		target=target_1+str(i)+target_2
		#print(target)										#每一分页面的链接
		html=requests.get(url=target)
		bf=BeautifulSoup(html.text,features='lxml')
		body=bf.find('ul',class_='info clearfix')
		li=body.find_all('li')
		#print(data)
		for li_item in li:
			a=li_item.find_all('a')
			span=li_item.find('span')
			if a[0]['href'][1]=='n':
				class_web_addr=addr_1+a[0]['href']		#原网页链接
			else :
				continue											#若不是校内网站，则跳过
			count=0
			class_title=a[0].get_text().strip()
			class_date=span.get_text().strip()
			xinwendongtai_list.append(xinwendongtai(title=class_title,date=class_date,web_addr=class_web_addr))
			xinwendongtai_list[-1].show()
		i=i+1
		if i==5:					        			#跳出页面
			break
	return xinwendongtai_list


'''print(get_zhaopinghui_list())
print(get_yk_zhaopinhui_list())
print(get_zhaopinxinxi_list())	
print(get_yk_zhaopinxinxi_list())
print(get_tongzhigonggao_list())
print(get_xinwendongtai_list())'''
