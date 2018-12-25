import pymysql
import msql
import time
from hust_jwc_text import get_jwc_text
from hust_jyxxw_text import get_jyxxw_text
from get_inter_text import get_inter_text
from get_access import get_access
from get_news import get_news_text
#last_url={'zhaopihui':'https://dsdsd','',....}

msql.creat_pool()#共用一个连接
while True:
	t = time.time()
	
	lst = get_jwc_text()
	for ls in lst:
		try:
			ls.save('jwc')
		except:
			ls.show()
			
	lst = get_jyxxw_text(1)
	for ls in lst:
		try:
			ls.save('zph')
		except:
			ls.show()
	
	lst = get_jyxxw_text(5)
	for ls in lst:
		try:
			ls.save('zph')
		except:
			ls.show()
	
	lst = get_inter_text()
	for ls in lst:
		try:
			ls.save('inter')
		except:
			ls.show()
			
	lst = get_news_text(1)
	for ls in lst:
		try:
			ls.save('lecture')
		except:
			ls.show()
			
	print('%f s'%(time.time()-t))
	get_access()#得到ip 动作
	time.sleep(500)
	
















