import requests
from bs4 import BeautifulSoup 
import get_inter
from msql import mysql

########传入对象列表，输出mysql列表#####
def get_inter_text():	
	class_list= get_inter.get_inter_xinxi()
	mysql_list=[]
	for item in class_list:	
		#############存入mysql类对象中########
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
		#########tim为空，place为空#####
		text=''
		class_content='['
		html=requests.get(url=item.web_addr)
		bf=BeautifulSoup(html.text,features='lxml')
		body=bf.find('div',attrs={"class": "col-main right"})
		'''###########获取标题########
		title=body.find('div',attrs={"class": "content_title"})
		class_title=title.get_text()'''
		############获取附件链接#######
		try:
			a=body.find_all('a')
			attach_addr=body.find('div',attrs={'style':"margin: 10px 20px; height: 18px;"})
			not_a=attach_addr.find_all('a')
			for a_item in a:
				if a_item in not_a:						######排除非附件内容
					continue
				class_content+=("{\"type\":\"url\",\"content\":\"附件,"+a_item['href']+"\"},")
		except:
			print('error')
		############获取文本########
		'''p=body.find_all('p')
		for p_item in p:
			text=text+(p_item.get_text().replace(' ','')+'\n')
		#print(text)
		class_content+=("{'type':'text','content':"+text+"}]")'''
		text_body=body.find('div',class_='content_body')
		class_content+="{\"type\":\"text\",\"content\":\""+text_body.get_text()+"\"}]"
		###########存入mysql#########
		mysql_list.append(mysql( title=class_title,tim=class_tim, place=class_place,url=class_url,content=class_content))
	return mysql_list
