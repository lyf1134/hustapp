import requests
from bs4 import BeautifulSoup
import hust_jyxxw
from msql import mysql
		
#############输入（jyxxw目录）对象列表，返回mysql对象列表#######
def get_jyxxw_text(id):
	if id == 1:
		class_list = hust_jyxxw.get_zhaopinhui_list()
	elif id == 2:
		class_list = hust_jyxxw.get_yk_zhaopinhui_list()
	elif id == 3:
		class_list = hust_jyxxw.get_zhaopinxinxi_list()
	elif id == 4:
		class_list = hust_jyxxw.get_yk_zhaopinxinxi_list()
	elif id == 5:
		class_list = hust_jyxxw.get_shixishengxinxi_list()
	elif id == 6:
		class_list = hust_jyxxw.get_tongzhigonggao_list()
	elif id == 7:
		class_list = hust_jyxxw.get_xinwendongtai_list()
	mysql_list=[]
#######################文本处理函数段#################
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
		#################################
		class_content=[]
		target_item=item.web_addr
		#print(target_item)
		class_content='['
		table_p=[]									#用于清除表格的文字	
		html=requests.get(url=target_item)
		bf=BeautifulSoup(html.text,features="lxml")
#############找到主要文章内容标签###内容标签有两种############
		body=bf.find_all('div',style="font-size:19px;font-family:宋体")
		if len(body)==0:
			body=bf.find_all('div',class_='txt')
		##############试图寻找table####以源代码形式输出##############
		try:
			table=body[0].find_all('table')
			for table_item in table:
				class_content+=("{\"type\":\"table\",\"content\":\""+str(table_item).replace('\"','\'')+"\"},")				#输出表格信息
				table_p.extend(table_item.find_all('p'))								#获取table里的p标签，元素为p标签
		except:
			pass
		p_tag=body[0].find_all('p')
		count=0																	
		print_point=0													#重复表格提示（详情见下表）
		text=""															#文本信息
		for p_tag_item in p_tag:
			count+=1
			if p_tag_item in table_p:									#判断是否在表格标签下,若是，则不输入到文本
				if count-print_point==1:
					print_point=count
				else:
					text+='\n详情见下表\n '
					print_point=count
				continue
			text+=(p_tag_item.get_text()+'\n')	
		class_content+=("{\"type\":\"text\",\"content\":\""+text+"\"}")
		class_content+=(']')
		mysql_list.append(mysql( title=class_title,tim=class_tim, place=class_place,url=class_url,content=class_content))
		mysql_list.reverse()
	return mysql_list
