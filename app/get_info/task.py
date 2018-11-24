import pymysql
import msql
import time
from hust_jwc_text import get_jwc_text
from hust_jyxxw_text import get_jyxxw_text
#last_url={'zhaopihui':'https://dsdsd','',....}

msql.creat_pool()
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
	print('%f s'%(time.time()-t))
	time.sleep(500)

















