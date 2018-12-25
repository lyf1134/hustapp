'''
sss='#0015433267941360ba1bbdf723d4d4fbf978644749297fd00#0015433267941360ba1bbdf723d4d4fbf978644749297fd001#0015433267941360ba1bbdf723d4d4fbf978644749297fd000'
id = '0015433267941360ba1bbdf723d4d4fbf978644749297fd000'
num = 0
str = sss
t = str.find('#')
while(t!=-1):
	num+=1
	str = str[t+1:]
	t = str.find('#')
print(num)
''''''
def find_at(uid,content):
	s=content.find('@ ')
	while s !=-1:
		e = content[s+2:].find(' ')
		user = content[s+2:s+3+e]
		print(user)
		content = content[s+3+e:]
		s = content.find('@ ')
	return
content="你好啊 @ ssskj hhh\n @asdsad\n @ ffgh \n"
find_at(1,content)
'''
import requests
import json
import re

url ='http://127.0.0.1/api/likes'
#data ={'school_num': 'U200000000', 'passwd': 'bc0181b0449c802ac7716edaed878d68a6a3af13'}
cookies={'husterqx':'0015430613007934daf4704fa23466f97331c74fef4a09c000-1544855556-cc6c372b944c1608c05f13ef654f625ca3bebbec'}
data = {'id':'00154366158021132f4d7c3bc7a47c9b0d791ae68502bea000','ku':'zph','uid':'U200000000'}
r = requests.post(url=url,data=data,cookies=cookies)
stri = r.content

#s = json.loads(s)[1]['content']
print(stri)

'''
content='[{"type":"text","content":"XX"}]'
print(content[0:27]+content[-3:])
if not content[0:27]+content[-3:]=='[{"type":"text","content":""}]':
	print(1)
else:
	print(2)
'''
