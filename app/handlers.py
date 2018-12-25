import re, time, json, logging, hashlib, base64, asyncio
from coroweb import get, post
from models import User, Comment, Jwc, next_id, Zph, Inter,Question,Lecture,Info
from apis import Page,APIValueError, APIResourceNotFoundError,APIPermissionError,APIError
from config import configs
from aiohttp import web
import markdown2

COOKIE_NAME = 'husterqx'
_COOKIE_KEY = configs.session.secret

def check_admin(request):#管理员
	if request.__user__ is None or not request.__user__.admin:
		raise APIPermissionError(message="You don't have permission to access")
		
def check_user(request,id):#管理/本人
	if request.__user__.admin:
		return
	if request.__user__ is None or request.__user__.id != id:
		raise APIPermissionError(message="You don't have permission to access")

def errors(id):#4种error类型
	if id == 1:
		raise APIValueError('content')
	elif id == 2:
		raise APIResourceNotFoundError('Comment')
	elif id == 3:
		raise APIPermissionError(message="You don't have permission to access")
	elif id == 4:
		raise APIError(4,'register:failed', 'school_num', 'School_num is already in use.')
		
async def find_at(uid,content):#寻找@
	s=content.find('@ ')
	while s !=-1:
		e = content[s+2:].find(' ')
		user = content[s+2:s+3+e]
		users = await User.findAll('name=?', [user])
		if len(users) == 0:
			raise APIValueError('user', 'user do not exit.')
		users[0].message+='#%s'%uid
		await users[0].update()
		content = content[s+3+e:]
		s = content.find('@ ')
		
async def get_likes(uid,ku,id):#得到点赞数
	if ku == 'jwc':
		essays = await Jwc.findAll('id=?',[id])
	elif ku == 'zph':
		essays = await Zph.findAll('id=?',[id])
	elif ku == 'inter':
		essays = await Inter.findAll('id=?',[id])
	elif ku == 'lecture':
		essays = await Lecture.findAll('id=?',[id])
	elif ku == 'info':
		essays = await Info.findAll('id=?',[id])
	if len(essays) == 0:
		raise APIResourceNotFoundError('%s essays'%ku)
	essay = essays[0]
	if essay.likes==None:
		like = dict(num=0,like=False)
	else:
		s = essay.likes.find('#%s'%uid)
		num = 0
		str = essay.likes
		t = str.find('#')
		while(t!=-1):
			num+=1
			str = str[t+1:]
			t = str.find('#')
		if s == -1:
			like = dict(num=num,like=False)
		else:
			like = dict(num=num,like=True)
	return like	
	
async def change_likes(uid,ku,id):#点赞/取消
	if ku == 'jwc':
		essays = await Jwc.findAll('id=?',[id])
	elif ku == 'zph':
		essays = await Zph.findAll('id=?',[id])
	elif ku == 'inter':
		essays = await Inter.findAll('id=?',[id])
	elif ku == 'lecture':
		essays = await Lecture.findAll('id=?',[id])
	elif ku == 'info':
		essays = await Info.findAll('id=?',[id])
	if len(essays) == 0:
		raise APIResourceNotFoundError('%s essays'%ku)
	essay = essays[0]
	if essay.likes==None:
		essay.likes='#%s'%uid
		like = dict(num =1,like=True)
	else:
		s = essay.likes.find('#%s'%uid)
		num = 0
		t = str.find('#')
		while(t!=-1):
			num+=1
			str = str[t+1:]
			t = str.find('#')
		if s == -1:
			essay.likes+='#%s'%uid
			like = dict(num =num,like=True)
		else:
			essay.likes=essay.likes[0:s]+essay.likes[s+len(uid)+1:]
			like = dict(num =num,like=False)
	await essay.update()
	return like
	
def get_page_index(page_str):
	p = 1
	try :
		p = int(page_str)
	except ValueError as e:
		pass
	if p < 1:
		p = 1
	return p

def texttohtml(text):
	lines = map(lambda s: '<p>%s</p>' % s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'),filter(lambda s: s.strip() !=  '', text.split('\n')))
	return ''.join(lines)

		
def usertocookie(user, max_age):#制作cookie
	'''
	Generate cookie str by user.
	'''
	# build cookie string by: id-expires-sha1
	expires = str(int(time.time() + max_age))
	s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
	L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	return '-'.join(L)


async def cookietouser(cookie_str):#解密
	'''
	Parse cookie and load user if cookie is valid.
	'''
	if not cookie_str:
		return None
	try:
		L = cookie_str.split('-')
		if len(L) != 3:
			return None
		uid, expires, sha1 = L
		if int(expires) < time.time():
			return None
		user = await User.find(uid)
		if user is None:
			return None
		s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
		if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
			logging.info('invalid sha1')
			return None
		user.passwd = '******'
		return user
	except Exception as e:
		logging.exception(e)
		return None

@get('/')
async def index(request):
	if request.__user__ and request.__user__.admin:
		return {
			'__template__': 'index.html',
			'__user__': request.__user__
		}
	else :
		return {
			'__template__': 'signin.html'
		}

@get('/user/{id}')
async def get_user(id,request):
	check_admin(request)
	user = await User.find(id)
	return {
		'__template__': 'user.html',
		'user': user
	}
	
@get('/user/{id}/change')
async def get_passwd_change(id,request):
	check_user(request,id)
	user = await User.find(id)
	return {
		'__template__': 'change_passwd.html',
		'user': user
	}	

@get('/register')
def register():
	return {
		'__template__': 'register.html'
	}

@get('/signin')
def signin():
	return {
		'__template__': 'signin.html'
	}

@post('/api/authenticate')#登陆
async def authenticate(*, school_num, passwd):
	#print(passwd)
	if not school_num:
		raise APIValueError('school_num', 'Invalid school_num.')
	if not passwd:
		raise APIValueError('passwd', 'Invalid password.')
	users = await User.findAll('school_num=?', [school_num])
	if len(users) == 0:
		raise APIValueError('school_num', 'School_num not exist.')
	user = users[0]
	# check passwd:
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	sha1.update(passwd.encode('utf-8'))
	if user.passwd != sha1.hexdigest():
		raise APIValueError('passwd', 'Invalid password.')
	# authenticate ok, set cookie:
	r = web.Response()
	r.set_cookie(COOKIE_NAME, usertocookie(user, 86400), max_age=86400, httponly=True)#刷新cookie
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	#print(r.body)
	return r

@get('/signout')
def signout(request):
	referer = request.headers.get('Referer')
	r = web.HTTPFound(referer or '/')
	r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
	logging.info('user signed out.')
	return r

@get('/manage/')
def manage():
	return 'redirect:/manage/comments'

@get('/manage/comments')
def manage_comments(*, page='1'):
	return {
		'__template__': 'manage_comments.html',
		'page_index': get_page_index(page)
	}
@get('/manage/questions')
def manage_questions(*, page='1'):
	return {
		'__template__': 'manage_questions.html',
		'page_index': get_page_index(page)
	}	
@get('/manage/comments/create')
def manage_create_comment():
	return {
		'__template__':'manage_comment_edit.html',
		'id': '',
		'action': '/api/comments'
	}	
@get('/manage/users')
def manage_users(*, page='1'):
	return {
		'__template__': 'manage_users.html',
		'page_index': get_page_index(page)
	}
	
_RE_NUM = re.compile(r'U20[0-1][0-9][0-2][0-9]{4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')
_RE_info =r'[{"type":"text","content":""}]'

@get('/api/users')
async def api_get_users(request,*,page='1'):
	check_admin(request)
	page_index = get_page_index(page)
	num = await User.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dirt(page=p, users=())
	users = await User.findAll(orderBy='created_at desc', limit=(p.offset,p.limit))
	for u in users:
		u.passwd = '******'
	return dict(code=0,page=p, users=users)

@get('/api/users/{id}')
async def api_get_user(request,*, id):
	check_user(request,id)
	user = await User.find(id)
	return dict(code=0,user=user)
	
@post('/api/users')#注册
async def api_register_user(*, school_num, name, passwd):
	if not name or not name.strip():
		raise APIValueError('name')
	if not school_num or not _RE_NUM.match(school_num):
		raise APIValueError('school_num')
	if not passwd or not _RE_SHA1.match(passwd):
		raise APIValueError('passwd')
	users = await User.findAll('school_num=?', [school_num])
	if len(users) > 0:
		raise APIError(4,'register:failed', 'school_num', 'School_num is already in use.')
	uid = next_id()
	sha1_passwd = '%s:%s' % (uid, passwd)
	user = User(id=uid, name=name.strip(), school_num=school_num, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(school_num.encode('utf-8')).hexdigest())
	await user.save()
	# make session cookie:
	r = web.Response()
	r.set_cookie(COOKIE_NAME, usertocookie(user, 86400), max_age=86400, httponly=True)#存cookie
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	#print(r.body)
	return r

@post('/api/users/{id}')
async def api_change_passwd(request,*,id,oldpasswd,newpasswd):#改密码
	check_user(request,id)
	if not oldpasswd or not _RE_SHA1.match(oldpasswd):
		raise APIValueError('oldpasswd')
	if not newpasswd or not _RE_SHA1.match(newpasswd):#符合sha1
		raise APIValueError('newpasswd')
	users = await User.findAll('id=?', [id])
	if len(users) == 0:
		raise APIError(4,'change passwd failed', 'user', 'user is not exist.')
	user=users[0]
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	sha1.update(oldpasswd.encode('utf-8'))
	if user.passwd != sha1.hexdigest():#比较
		raise APIValueError('passwd', 'Invalid password.')
	sha1_newpasswd = '%s:%s' % (id, newpasswd)
	user.passwd = hashlib.sha1(sha1_newpasswd.encode('utf-8')).hexdigest()
	await user.update()
	# make session cookie:
	r = web.Response()
	r.set_cookie(COOKIE_NAME, usertocookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	#print(r.body)
	return r
	
@post('/api/users/{id}/delete')#删除
async def api_delete_users(id, request):
	check_admin(request)
	user = await User.find(id)
	if user is None:
		raise APIResourceNotFoundError('User')
	await user.remove()
	return dict(id=id)	
#-------------------------------------------------#教务处
@get('/jwc/{id}')
async def get_jwc(id):#得到信息与评论
	jwc = await Jwc.find(id)
	comments = await Comment.findAll('xinxi_id=?',[id],orderBy='created_at desc')
	for c in comments:
		c.html_content = texttohtml(c.content)
	jwc.html_content = markdown2.markdown(jwc.content)#jwc.content
	return{
		'__template__': 'jwc.html',
		'jwc': jwc,
		'comments': comments
	}
	
@get('/manage/jwcs')
def manage_jwcs(*,page='1'):
	return {
		'__template__': 'manage_jwcs.html',
		'page_index': get_page_index(page),
		'XXX':'jwc'
	}
	
@get('/manage/jwcs/create')
def manage_create_jwc():
	return {
		'__template__':'manage_jwc_edit.html',
		'id': '',
		'action': '/api/jwcs'
	}
	
@get('/manage/jwcs/edit')
def manage_edit_jwc(*, id):
	return {
		'__template__': 'manage_jwc_edit.html',
		'id': id,
		'action': '/api/jwcs/%s' % id
	}	
	
@get('/api/time/jwcs')
async def api_jwcs_time():#更新时间
	jwcs = await Jwc.finded('max(created_at)')
	return dict(code=0, time=jwcs['max(created_at)'])

@get('/api/jwcs')
async def api_jwcs(request,*, page='1'):
	#check_admin(request)
	page_index = get_page_index(page)
	num = await Jwc.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, jwcs=())
	jwcs = await Jwc.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	for jwc in jwcs:
		jwc.content=json.loads(jwc.content, strict=False)
		for con in jwc.content:
			if con['type'] == 'text':
				con['content']=con['content'][0:20]
	return dict(code=0,page=p, items=jwcs)

@get('/api/jwcs/{id}')
async def api_get_jwc(*, id):
	jwc = await Jwc.find(id)
	jwc.content=json.loads(jwc.content, strict=False)
	comments = await Comment.findAll('xinxi_id=?',[id],orderBy='created_at desc')
	return dict(code=0,items=jwc,comments=comments)
	
@get('/api/jwcs/{id}/edit')
async def api_jwc_edit(*, id):
	jwc = await Jwc.find(id)
	return dict(code=0,jwc=jwc)
	
@post('/api/jwcs')
async def api_create_jwc(request, *, title, tim, place, url, content):#新建
	check_admin(request)
	if not title or not title.strip():
		raise APIValueError('title', 'title cannot be empty.')
	if not tim or not tim.strip():
		raise APIValueError('tim', 'tim cannot be empty.')
	if not place or not place.strip():
		raise APIValueError('place', 'place cannot be empty.')
	if not url or not url.strip():
		raise APIValueError('url', 'url cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	jwc = Jwc(title=title.strip(),tim=tim.strip(),place=place.strip(), url=url.strip(), content=content.strip())
	await jwc.save()
	return jwc

@post('/api/jwcs/{id}')
async def api_update_jwc(id, request, *, title, tim, place, url, content):#修改
	check_admin(request)
	jwc = await Jwc.find(id)
	if not title or not title.strip():
		raise APIValueError('title', 'title cannot be empty.')
	if not tim or not tim.strip():
		raise APIValueError('tim', 'tim cannot be empty.')
	if not place or not place.strip():
		raise APIValueError('place', 'place cannot be empty.')
	if not url or not url.strip():
		raise APIValueError('url', 'url cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	jwc.title = title.strip()
	jwc.tim = tim.strip()
	jwc.place = place.strip()
	jwc.url = url.strip()
	jwc.content = content.strip()
	await jwc.update()
	return jwc
	
@post('/api/jwcs/{id}/delete')
async def api_delete_jwc(request, *, id):#删除
	check_admin(request)
	jwc = await Jwc.find(id)
	await jwc.remove()
	return dict(id=id)
	
@post('/api/jwcs/{id}/comments')
async def api_create_jwc_comment(id, request, *, content):#新建评论
	user = request.__user__
	if user is None:
		raise APIPermissionError('Please signin first.')
	if not content or not content.strip():
		raise APIValueError('content')
	jwc = await Jwc.find(id)
	if jwc is None:
		raise APIResourceNotFoundError('jwc')
	uid = next_id()
	await find_at(uid,content)
	comment = Comment(id=uid,xinxi_id=jwc.id,user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip(), ku='jwc')
	await comment.save()
	return dict(code=0,comment=comment)
#-------------------------------------------------#留学
@get('/inter/{id}')
async def get_inter(id):
	inter = await Inter.find(id)
	comments = await Comment.findAll('xinxi_id=?',[id],orderBy='created_at desc')
	for c in comments:
		c.html_content = texttohtml(c.content)
	inter.html_content = markdown2.markdown(inter.content)#inter.content
	return{
		'__template__': 'inter.html',
		'inter': inter,
		'comments': comments
	}
	
@get('/manage/inters')
def manage_inters(*,page='1'):
	return {
		'__template__': 'manage_inters.html',
		'page_index': get_page_index(page),
		'XXX':'inter'
	}
	
@get('/manage/inters/create')
def manage_create_inter():
	return {
		'__template__':'manage_inter_edit.html',
		'id': '',
		'action': '/api/inters'
	}
	
@get('/manage/inters/edit')
def manage_edit_inter(*, id):
	return {
		'__template__': 'manage_inter_edit.html',
		'id': id,
		'action': '/api/inters/%s' % id
	}	
	
@get('/api/time/inters')
async def api_inters_time():
	inters = await Inter.finded('max(created_at)')
	return dict(code=0, time=inters['max(created_at)'])

@get('/api/inters')
async def api_inters(request,*, page='1'):
	#check_admin(request)
	page_index = get_page_index(page)
	num = await Inter.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, inters=())
	inters = await Inter.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	for inter in inters:
		inter.content=json.loads(inter.content, strict=False)
		for con in inter.content:
			if con['type'] == 'text':
				con['content']=con['content'][0:20]
	return dict(code=0,page=p, items=inters)

@get('/api/inters/{id}')
async def api_get_inter(*, id):
	inter = await Inter.find(id)
	inter.content=json.loads(inter.content, strict=False)
	comments = await Comment.findAll('xinxi_id=?',[id],orderBy='created_at desc')
	return dict(code=0,items=inter,comments=comments)

@get('/api/inters/{id}/edit')
async def api_inter_edit(*, id):
	inter = await Inter.find(id)
	return dict(code=0,inter=inter)	
	
@post('/api/inters')
async def api_create_inter(request, *, title, tim, place, url, content):
	check_admin(request)
	if not title or not title.strip():
		raise APIValueError('title', 'title cannot be empty.')
	if not tim or not tim.strip():
		raise APIValueError('tim', 'tim cannot be empty.')
	if not place or not place.strip():
		raise APIValueError('place', 'place cannot be empty.')
	if not url or not url.strip():
		raise APIValueError('url', 'url cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	inter = Inter(title=title.strip(),tim=tim.strip(),place=place.strip(), url=url.strip(), content=content.strip())
	await inter.save()
	return inter

@post('/api/inters/{id}')
async def api_update_inter(id, request, *, title, tim, place, url, content):
	check_admin(request)
	inter = await Inter.find(id)
	if not title or not title.strip():
		raise APIValueError('title', 'title cannot be empty.')
	if not tim or not tim.strip():
		raise APIValueError('tim', 'tim cannot be empty.')
	if not place or not place.strip():
		raise APIValueError('place', 'place cannot be empty.')
	if not url or not url.strip():
		raise APIValueError('url', 'url cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	inter.title = title.strip()
	inter.tim = tim.strip()
	inter.place = place.strip()
	inter.url = url.strip()
	inter.content = content.strip()
	await inter.update()
	return inter
	
@post('/api/inters/{id}/delete')
async def api_delete_inter(request, *, id):
	check_admin(request)
	inter = await Inter.find(id)
	await inter.remove()
	return dict(id=id)
	
@post('/api/inters/{id}/comments')
async def api_create_inter_comment(id, request, *, content):
	user = request.__user__
	if user is None:
		raise APIPermissionError('Please signin first.')
	if not content or not content.strip():
		raise APIValueError('content')
	inter = await Inter.find(id)
	if inter is None:
		raise APIResourceNotFoundError('inter')
	uid = next_id()
	await find_at(uid,content)
	comment = Comment(id=uid,xinxi_id=inter.id,ku='inter',user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
	await comment.save()
	return dict(code=0,comment=comment)
#-------------------------------------------------#招聘
@get('/zph/{id}')
async def get_zph(id):
	zph = await Zph.find(id)
	comments = await Comment.findAll('xinxi_id=?',[id],orderBy='created_at desc')
	for c in comments:
		c.html_content = texttohtml(c.content)
	zph.html_content = markdown2.markdown(zph.content)#zph.content
	return{
		'__template__': 'zph.html',
		'zph': zph,
		'comments': comments
	}
	
@get('/manage/zphs')
def manage_zphs(*,page='1'):
	return {
		'__template__': 'manage_zphs.html',
		'page_index': get_page_index(page),
		'XXX':'zph'
	}
	
@get('/manage/zphs/create')
def manage_create_zph():
	return {
		'__template__':'manage_zph_edit.html',
		'id': '',
		'action': '/api/zphs'
	}
	
@get('/manage/zphs/edit')
def manage_edit_zph(*, id):
	return {
		'__template__': 'manage_zph_edit.html',
		'id': id,
		'action': '/api/zphs/%s' % id
	}	
	
@get('/api/time/zphs')
async def api_zphs_time():
	zphs = await Zph.finded('max(created_at)')
	return dict(code=0, time=zphs['max(created_at)'])

@get('/api/zphs')
async def api_zphs(request,*, page='1'):
	#check_admin(request)
	page_index = get_page_index(page)
	num = await Zph.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, zphs=())
	zphs = await Zph.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	for zph in zphs:
		zph.content=json.loads(zph.content, strict=False)
		for con in zph.content:
			if con['type'] == 'text':
				con['content']=con['content'][0:20]
			if con['type'] == 'table':
				con['content']=' '
	return dict(code=0,page=p, items=zphs)

@get('/api/zphs/{id}')
async def api_get_zph(*, id):
	zph = await Zph.find(id)
	zph.content=json.loads(zph.content, strict=False)
	comments = await Comment.findAll('xinxi_id=?',[id],orderBy='created_at desc')
	return dict(code=0,items=zph,comments=comments)

@get('/api/zphs/{id}/edit')
async def api_zph_edit(*, id):
	zph = await Zph.find(id)
	return dict(code=0,zph=zph)	
	
@post('/api/zphs')
async def api_create_zph(request, *, title, tim, place, url, content):
	check_admin(request)
	if not title or not title.strip():
		raise APIValueError('title', 'title cannot be empty.')
	if not tim or not tim.strip():
		raise APIValueError('tim', 'tim cannot be empty.')
	if not place or not place.strip():
		raise APIValueError('place', 'place cannot be empty.')
	if not url or not url.strip():
		raise APIValueError('url', 'url cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	zph = Zph(title=title.strip(),tim=tim.strip(),place=place.strip(), url=url.strip(), content=content.strip())
	await zph.save()
	return zph

@post('/api/zphs/{id}')
async def api_update_zph(id, request, *, title, tim, place, url, content):
	check_admin(request)
	zph = await Zph.find(id)
	if not title or not title.strip():
		raise APIValueError('title', 'title cannot be empty.')
	if not tim or not tim.strip():
		raise APIValueError('tim', 'tim cannot be empty.')
	if not place or not place.strip():
		raise APIValueError('place', 'place cannot be empty.')
	if not url or not url.strip():
		raise APIValueError('url', 'url cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	zph.title = title.strip()
	zph.tim = tim.strip()
	zph.place = place.strip()
	zph.url = url.strip()
	zph.content = content.strip()
	await zph.update()
	return zph
	
@post('/api/zphs/{id}/delete')
async def api_delete_zph(request, *, id):
	check_admin(request)
	zph = await Zph.find(id)
	await zph.remove()
	return dict(id=id)
	
@post('/api/zphs/{id}/comments')
async def api_create_zph_comment(id, request, *, content):
	user = request.__user__
	if user is None:
		raise APIPermissionError('Please signin first.')
	if not content or not content.strip():
		raise APIValueError('content')
	zph = await Zph.find(id)
	if zph is None:
		raise APIResourceNotFoundError('zph')
	uid = next_id()
	await find_at(uid,content)
	comment = Comment(id=uid,xinxi_id=zph.id,ku='zph', user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
	await comment.save()
	return dict(code=0,comment=comment)

	
#-------------------------------------------------#讲座
@get('/lecture/{id}')
async def get_lecture(id):
	lecture = await Lecture.find(id)
	comments = await Comment.findAll('xinxi_id=?',[id],orderBy='created_at desc')
	for c in comments:
		c.html_content = texttohtml(c.content)
	lecture.html_content = markdown2.markdown(lecture.content)#lecture.content
	return{
		'__template__': 'lecture.html',
		'lecture': lecture,
		'comments': comments
	}
	
@get('/manage/lectures')
def manage_lectures(*,page='1'):
	return {
		'__template__': 'manage_lectures.html',
		'page_index': get_page_index(page),
		'XXX':'lecture'
	}
	
@get('/manage/lectures/create')
def manage_create_lecture():
	return {
		'__template__':'manage_lecture_edit.html',
		'id': '',
		'action': '/api/lectures'
	}
	
@get('/manage/lectures/edit')
def manage_edit_lecture(*, id):
	return {
		'__template__': 'manage_lecture_edit.html',
		'id': id,
		'action': '/api/lectures/%s' % id
	}	
	
@get('/api/time/lectures')
async def api_lectures_time():
	lectures = await Lecture.finded('max(created_at)')
	return dict(code=0, time=lectures['max(created_at)'])

@get('/api/lectures')
async def api_lectures(request,*, page='1'):
	#check_admin(request)
	page_index = get_page_index(page)
	num = await Lecture.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, lectures=())
	lectures = await Lecture.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	for lecture in lectures:
		lecture.content=json.loads(lecture.content, strict=False)
		for con in lecture.content:
			if con['type'] == 'text':
				con['content']=con['content'][0:20]
	return dict(code=0,page=p, items=lectures)

@get('/api/lectures/{id}')
async def api_get_lecture(*, id):
	lecture = await Lecture.find(id)
	lecture.content=json.loads(lecture.content, strict=False)
	comments = await Comment.findAll('xinxi_id=?',[id],orderBy='created_at desc')
	return dict(code=0,items=lecture,comments=comments)

@get('/api/lectures/{id}/edit')
async def api_lecture_edit(*, id):
	lecture = await Lecture.find(id)
	return dict(code=0,lecture=lecture)
	
@post('/api/lectures')
async def api_create_lecture(request, *, title, tim, place, url, content):
	check_admin(request)
	if not title or not title.strip():
		raise APIValueError('title', 'title cannot be empty.')
	if not tim or not tim.strip():
		raise APIValueError('tim', 'tim cannot be empty.')
	if not place or not place.strip():
		raise APIValueError('place', 'place cannot be empty.')
	if not url or not url.strip():
		raise APIValueError('url', 'url cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	lecture = Lecture(title=title.strip(),tim=tim.strip(),place=place.strip(), url=url.strip(), content=content.strip())
	await lecture.save()
	return lecture

@post('/api/lectures/{id}')
async def api_update_lecture(id, request, *, title, tim, place, url, content):
	check_admin(request)
	lecture = await Lecture.find(id)
	if not title or not title.strip():
		raise APIValueError('title', 'title cannot be empty.')
	if not tim or not tim.strip():
		raise APIValueError('tim', 'tim cannot be empty.')
	if not place or not place.strip():
		raise APIValueError('place', 'place cannot be empty.')
	if not url or not url.strip():
		raise APIValueError('url', 'url cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	lecture.title = title.strip()
	lecture.tim = tim.strip()
	lecture.place = place.strip()
	lecture.url = url.strip()
	lecture.content = content.strip()
	await lecture.update()
	return lecture
	
@post('/api/lectures/{id}/delete')
async def api_delete_lecture(request, *, id):
	check_admin(request)
	lecture = await Lecture.find(id)
	await lecture.remove()
	return dict(id=id)
	
@post('/api/lectures/{id}/comments')
async def api_create_lecture_comment(id, request, *, content):
	user = request.__user__
	if user is None:
		raise APIPermissionError('Please signin first.')
	if not content or not content.strip():
		raise APIValueError('content')
	lecture = await Lecture.find(id)
	if lecture is None:
		raise APIResourceNotFoundError('lecture')
	uid = next_id()
	await find_at(uid,content)
	comment = Comment(id=uid,xinxi_id=lecture.id,ku='lecture', user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
	await comment.save()
	return dict(code=0,comment=comment)
#-------------------------------------------------#情报
@get('/info/{id}')
async def get_info(id):
	info = await Info.find(id)
	comments = await Comment.findAll('xinxi_id=?',[id],orderBy='created_at desc')
	for c in comments:
		c.html_content = texttohtml(c.content)
	info.html_content = markdown2.markdown(info.content)#info.content
	return{
		'__template__': 'info.html',
		'info': info,
		'comments': comments
	}
	
@get('/manage/infos')
def manage_infos(*,page='1'):
	return {
		'__template__': 'manage_infos.html',
		'page_index': get_page_index(page),
		'XXX':'info'
	}
	
@get('/manage/infos/create')
def manage_create_info():
	return {
		'__template__':'manage_info_edit.html',
		'id': '',
		'action': '/api/infos'
	}
	
@get('/manage/infos/edit')
def manage_edit_info(*, id):
	return {
		'__template__': 'manage_info_edit.html',
		'id': id,
		'action': '/api/infos/%s' % id
	}	
	
@get('/api/time/infos')
async def api_infos_time():
	infos = await Info.finded('max(created_at)')
	return dict(code=0, time=infos['max(created_at)'])

@get('/api/infos')
async def api_infos(request,*, page='1'):
	page_index = get_page_index(page)
	num = await Info.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, infos=())
	infos = await Info.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	for info in infos:
		info.content=json.loads(info.content, strict=False)
		for con in info.content:
			if con['type'] == 'text':
				con['content']=con['content'][0:20]
	return dict(code=0,page=p, items=infos)

@get('/api/infos/0/study')
async def api_infos_study(request,*, page='1'):
	page_index = get_page_index(page)
	num = await Info.findNumber('count(id)',where="_type_ = 'study'")
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, infos=())
	infos = await Info.findAll(orderBy='created_at desc',where="_type_ = 'study'", limit=(p.offset, p.limit))
	for info in infos:
		info.content=json.loads(info.content, strict=False)
		for con in info.content:
			if con['type'] == 'text':
				con['content']=con['content'][0:20]
	return dict(code=0,page=p, items=infos)

@get('/api/infos/0/life')
async def api_infos_life(request,*, page='1'):
	page_index = get_page_index(page)
	num = await Info.findNumber('count(id)',where="_type_ = 'life'")
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, infos=())
	infos = await Info.findAll(orderBy='created_at desc',where="_type_ = 'life'", limit=(p.offset, p.limit))
	for info in infos:
		info.content=json.loads(info.content, strict=False)
		for con in info.content:
			if con['type'] == 'text':
				con['content']=con['content'][0:20]
	return dict(code=0,page=p, items=infos)

@get('/api/infos/0/club')
async def api_infos_club(request,*, page='1'):
	page_index = get_page_index(page)
	num = await Info.findNumber('count(id)',where="_type_ = 'club'")
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, infos=())
	infos = await Info.findAll(orderBy='created_at desc',where="_type_ = 'club'", limit=(p.offset, p.limit))
	for info in infos:
		info.content=json.loads(info.content, strict=False)
		for con in info.content:
			if con['type'] == 'text':
				con['content']=con['content'][0:20]
	return dict(code=0,page=p, items=infos)

@get('/api/infos/0/need')
async def api_infos_need(request,*, page='1'):
	page_index = get_page_index(page)
	num = await Info.findNumber('count(id)',where="_type_ = 'need'")
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, infos=())
	infos = await Info.findAll(orderBy='created_at desc',where="_type_ = 'need'", limit=(p.offset, p.limit))
	for info in infos:
		info.content=json.loads(info.content, strict=False)
		for con in info.content:
			if con['type'] == 'text':
				con['content']=con['content'][0:20]
	return dict(code=0,page=p, items=infos)
	
@get('/api/infos/{id}')
async def api_get_info(*, id):
	info = await Info.find(id)
	info.content=json.loads(info.content, strict=False)
	comments = await Comment.findAll('xinxi_id=?',[id],orderBy='created_at desc')
	return dict(code=0,items=info,comments=comments)

@get('/api/infos/{id}/edit')
async def api_info_edit(*, id):
	info = await Info.find(id)
	return dict(code=0,info=info)	
	
@post('/api/infos')
async def api_create_info(request, *, title, _type_ ,content):
	check_admin(request)
	if not title or not title.strip():
		raise APIValueError('title', 'title cannot be empty.')
	if not _type_ or not _type_.strip():
		raise APIValueError('_type_', '_type_ cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	if not content[0:27]+content[-3:]== _RE_info:
		raise APIValueError('content', 'content format error')
	info = Info(title=title.strip(),_type_=_type_, content=content.strip())
	await info.save()
	return info

@post('/api/infos/{id}')
async def api_update_info(id, request, *, title,_type_,content):
	check_admin(request)
	info = await Info.find(id)
	if not title or not title.strip():
		raise APIValueError('title', 'title cannot be empty.')
	if not _type_ or not _type_.strip():
		raise APIValueError('_type_', '_type_ cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	if not content[0:27]+content[-3:]== _RE_info:
		raise APIValueError('content', 'content format error')
	info.title = title.strip()
	info._type_ = _type_.strip()
	info.content = content.strip()
	await info.update()
	return info
	
@post('/api/infos/{id}/delete')
async def api_delete_info(request, *, id):
	check_admin(request)
	info = await Info.find(id)
	await info.remove()
	return dict(id=id)
	
@post('/api/infos/{id}/comments')
async def api_create_info_comment(id, request, *, content):
	user = request.__user__
	if user is None:
		raise APIPermissionError('Please signin first.')
	if not content or not content.strip():
		raise APIValueError('content')
	info = await Info.find(id)
	if info is None:
		raise APIResourceNotFoundError('info')
	uid = next_id()
	await find_at(uid,content)
	comment = Comment(id=uid,xinxi_id=info.id,ku='info', user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
	await comment.save()
	return dict(code=0,comment=comment)

	
#-------------------------------------------------#
@get('/api/comments')
async def api_comments(*, page='1'):
	page_index = get_page_index(page)
	num = await Comment.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, comments=())
	comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	return dict(code=0,page=p, comments=comments)
	
@post('/api/comments')
async def api_create_comment(request, *,user,content):#新建系统消息
	check_admin(request)
	if not user or not user.strip():
		raise APIValueError('user', 'user cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	uid = next_id()
	if user == '*':
		users = await User.findAll(orderBy='created_at desc')
		for item in users:
			item.message+='#%s'%uid
			await item.update()
	else:
		users = await User.findAll('name=?', [user])
		if len(users) == 0:
			raise APIValueError('user', 'user do not exit.')
		users[0].message+='#%s'%uid
		await users[0].update()
	comment = Comment(id = uid,xinxi_id='0',ku=user, user_id='0', user_name='admin', user_image=' ' , content=content.strip())
	await comment.save()
	return comment
	
@get('/api/comments/{id}')
async def api_get_comment(*, id):
	comment = await Comment.find(id)
	return dict(code=0,comment=comment)	

@post('/api/comments/{id}/delete')#删除系统消息
async def api_delete_comments(id, request):
	check_admin(request)
	c = await Comment.find(id)
	if c is None:
		raise APIResourceNotFoundError('Comment')
	if c.xinxi_id=='0':
		user = c.ku
		if user == '*':
			users = await User.findAll(orderBy='created_at desc')
			for item in users:
				st=item.message.find('#%s'%id)
				item.message=item.message[0:st]+item.message[st+len(id)+1:]
				await item.update()
		else:
			users = await User.findAll('name=?', [user])
			if len(users) == 0:
				raise APIValueError('user', 'user do not exit.')
			st=users[0].message.find('#%s'%id)
			users[0].message=users[0].message[0:st]+users[0].message[st+len(id)+1:]
			await users[0].update()
	await c.remove()
	return dict(id=id)
	
@post('/api/messages/delete')#删除个人消息
async def api_delete_messges(request, *, id,uid):
	check_user(request,id)
	users = await User.findAll('id=?', [id])
	if len(users) == 0:
		raise APIValueError('user', 'user do not exit.')
	st=users[0].message.find('#%s'%uid)
	if st == -1:
		raise APIValueError('message', 'message do not exit.')
	users[0].message=users[0].message[0:st]+users[0].message[st+len(id)+1:]
	await users[0].update()
	return dict(code=0,uid=uid)	
	
@get('/api/questions')#查看反馈
async def api_questions(*, page='1'):
	page_index = get_page_index(page)
	num = await Question.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, questions=())
	questions = await Question.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	return dict(code=0,page=p, questions=questions)
	
@post('/api/questions')#提交反馈
async def api_creat_question(request,*,content):
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	user = request.__user__
	que = Question(user_id=user.id,user_name=user.name,content=content)
	await que.save()
	return dict(code=0,items=que)
	
@post('/api/questions/{id}/delete')#删除
async def api_delete_questions(id, request):
	check_admin(request)
	que = await Question.find(id)
	if que is None:
		raise APIResourceNotFoundError('Question')
	await que.remove()
	return dict(id=id)
	
@get('/api/errors/{id}')#测试
async def api_errors(id, request):
	errors(int(id))
	return 

@post('/api/likes/{id}')#获得点赞数及是否点赞
async def api_get_like(request, *, id,ku,uid):
	check_user(request,uid)
	if not id or not id.strip():
		raise APIValueError('id', 'id cannot be empty.')
	if not ku or not ku.strip():
		raise APIValueError('ku', 'ku cannot be empty.')
	if not uid or not uid.strip():
		raise APIValueError('uid', 'uid cannot be empty.')
	like=await get_likes(uid,ku,id)
	return dict(code=0,items=like)

@post('/api/likes')#点赞
async def api_change_likes(request, *, id,ku,uid):#点/灭
	check_user(request,uid)
	if not id or not id.strip():
		raise APIValueError('id', 'id cannot be empty.')
	if not ku or not ku.strip():
		raise APIValueError('ku', 'ku cannot be empty.')
	if not uid or not uid.strip():
		raise APIValueError('uid', 'uid cannot be empty.')
	like=await change_likes(uid,ku,id)	
	return dict(code=0,items=like)
