import requests
from bs4 import BeautifulSoup
import json
import time

url = 'http://jwc.hust.edu.cn/info/'
fl_list = ['1058','1208','1096','1135']
now = '6520'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
while 1:
	i = now
	for fl in fl_list:
		time.sleep(1)
		r = requests.get(url = url+fl+'/'+now+'.htm',headers=headers)
		print(r.status_code)
		print(now)
		if r.status_code == 200:
			try:
				html = r.text.encode(r.encoding).decode('utf-8')
				print(r.encoding)
				with open('list/'+now+'.txt','w+',encoding='utf-8') as f:
					f.write(html)
			except:
				print('爬'+now+'.html error')
			now = str(int(now)+1)
			break
	now = str(int(now)+1)
	if i == '6600':
		print('exit')
		break
