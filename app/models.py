import time, uuid
from orm import Model, StringField, BooleanField, FloatField, TextField

def next_id():
	return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
	__table__ = 'users'
	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	school_num = StringField(ddl='varchar(50)')
	passwd = StringField(ddl='varchar(50)')
	admin = BooleanField()
	name = StringField(ddl='varchar(50)')
	image = StringField(ddl='varchar(500)')
	message = TextField()
	content = StringField(default='无',ddl='varchar(500)')
	created_at = FloatField(default=time.time)

class Comment(Model):
	__table__ = 'comments'
	id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
	ku = StringField(ddl='varchar(50)')
	xinxi_id = StringField(ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	user_name = StringField(ddl='varchar(50)')
	user_image = StringField(ddl='varchar(500)')
	content = TextField()
	created_at = FloatField(default=time.time)

class Question(Model):
	__table__ = 'question'
	id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	user_name = StringField(ddl='varchar(50)')
	content = TextField()
	created_at = FloatField(default=time.time)
	
class Zph(Model):
	__table__ = 'zph'
	id = StringField(primary_key=True, default=next_id,ddl='varchar(10)')
	title = StringField(ddl='varchar(100)')
	tim = StringField(ddl='varchar(50)')
	place = StringField(ddl='varchar(50)')
	url = StringField(ddl='varchar(60)')
	content = TextField()
	likes = TextField()
	created_at = FloatField(default=time.time)
	
class Jwc(Model):
	__table__ = 'jwc'
	id = StringField(primary_key=True, default=next_id,ddl='varchar(10)')
	title = StringField(ddl='varchar(100)')
	tim = StringField(ddl='varchar(50)')
	place = StringField(ddl='varchar(50)')
	url = StringField(ddl='varchar(60)')
	content = TextField()
	likes = TextField()
	created_at = FloatField(default=time.time)
	
class Inter(Model):
	__table__ = 'inter'
	id = StringField(primary_key=True, default=next_id,ddl='varchar(10)')
	title = StringField(ddl='varchar(100)')
	tim = StringField(ddl='varchar(50)')
	place = StringField(ddl='varchar(50)')
	url = StringField(ddl='varchar(100)')
	content = TextField()
	likes = TextField()
	created_at = FloatField(default=time.time)

class Lecture(Model):
	__table__ = 'lecture'
	id = StringField(primary_key=True, default=next_id,ddl='varchar(10)')
	title = StringField(ddl='varchar(100)')
	tim = StringField(ddl='varchar(50)')
	place = StringField(ddl='varchar(50)')
	url = StringField(ddl='varchar(100)')
	content = TextField()
	likes = TextField()
	created_at = FloatField(default=time.time)
	
class Info(Model):
	__table__ = 'info'
	id = StringField(primary_key=True, default=next_id,ddl='varchar(10)')
	title = StringField(ddl='varchar(100)')
	_type_ = StringField(ddl='varchar(10)')
	content = TextField()
	likes = TextField()
	created_at = FloatField(default=time.time)