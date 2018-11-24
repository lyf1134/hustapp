import time,uuid
import pymysql

def next_id():
	return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)
def creat_pool():
	global __pool
	__pool = pymysql.connect("localhost", "root", "password", "test")
class mysql():
	def __init__(self, title,tim, place, url,content):
		self.title = title					#标题
		self.tim= tim						#发布时间		
		self.place = place					#实际举行地点	
		self.url = url						#网页信息链接
		self.content = content				#内容（包含table，text，url）
	def save(self,tables):
		sql="insert into %s" %tables+"(id,title,tim,place,url,content,created_at) values ('%s','%s','%s','%s','%s','%s',%s)"%(next_id(),self.title,self.tim,self.place,self.url,pymysql.escape_string(self.content),time.time())
		save_text(sql)
	def show(self):
		print(self.title,self.tim,self.place,self.url,self.content)
		
def save_text(sql):
	global __pool
	cur = __pool.cursor()
	# 执行sql语句
	try:
		cur.execute(sql)
	# 提交到数据库执行
		__pool.commit()
	# 发生错误时回滚
	except:
		__pool.rollback()