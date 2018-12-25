import requests
from bs4 import BeautifulSoup
import hust_jwc
from msql import mysql

def get_jwc_text():
	jwc_list=hust_jwc.get_jwc()
	addr='http://jwc.hust.edu.cn/'
	mysql_list=[]
	for item in jwc_list:
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
		html=requests.get(url=item.web_addr)
	###############编码与解码的问题##############
		text=html.text.encode(html.encoding).decode('utf-8')
		temp_text=''
		bf=BeautifulSoup(text,features='lxml')
	#################下载链接################
		li=bf.find_all('li')
		li=li[0:2]
		for li_item in li:
			temp_text=''
			a=li_item.find('a')
			temp_text+=(a.get_text()+',')
			temp_text+=(addr+a['href'])
			class_content+=("{\"type\":\"url\",\"content\":\""+temp_text+"\"},")
		temp_text=''
	###################文本信息#################
		table33=bf.find('table',attrs={"id": "table33"}) 
		p=table33.find_all('p')
		for p_item in p:
			if '点击率' in p_item.get_text():				#不显示点击率
				temp_text+=(p_item.get_text()[0:16]+'\n')
				continue
			if '<sign_start>'  in p_item.get_text():		#去除最后面的干扰项
				continue
			temp_text+=(p_item.get_text()+'\n')
		class_content+=("{\"type\":\"text\",\"content\":\""+temp_text+"\"}]")
		mysql_list.append(mysql( title=class_title,tim=class_tim, place=class_place,url=class_url,content=class_content))
		mysql_list.reverse()
	return mysql_list