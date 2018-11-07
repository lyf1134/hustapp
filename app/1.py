import requests
from bs4 import BeautifulSoup
import json
import time

url='http://jwc.hust.edu.cn/info/1208/6543.htm'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
r = requests.get(url = url,headers=headers)
print(r.text.encode(r.encoding).decode('utf-8'))
time.sleep(10)