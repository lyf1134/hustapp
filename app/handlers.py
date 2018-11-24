import re, time, json, logging, hashlib, base64, asyncio
from coroweb import get, post
from models import User, Comment, Blog, next_id,Jobs
from apis import Page,APIValueError, APIResourceNotFoundError,APIPermissionError
from config import configs
from aiohttp import web
import markdown2

COOKIE_NAME = 'husterqx'
_COOKIE_KEY = configs.session.secret

def check_admin(request):
	if request.__user__ is None or not request.__user__.admin:
		raise APIPermissionError(message="You don't have permission to access")
		
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

		
def usertocookie(user, max_age):
	'''
	Generate cookie str by user.
	'''
	# build cookie string by: id-expires-sha1
	expires = str(int(time.time() + max_age))
	s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
	L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	return '-'.join(L)


async def cookietouser(cookie_str):
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
async def index(request, *, page='1'):
	page_index = get_page_index(page)
	num = await Blog.findNumber('count(id)')
	page = Page(num)
	if num == 0:
		blogs = []
	else:
		blogs = await Blog.findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
	return {
		'__template__': 'blogs.html',
		'page': page,
		'blogs': blogs,
		'__user__': request.__user__
	}

@get('/blog/{id}')
async def get_blog(id):
	blog = await Blog.find(id)
	comments = await Comment.findAll('blog_id=?',[id],orderBy='created_at desc')
	for c in comments:
		c.html_content = texttohtml(c.content)
	blog.html_content = markdown2.markdown(blog.content)
	return{
		'__template__': 'blog.html',
		'blog': blog,
		'comments': comments
	}

@get('/user/{id}')
async def get_user(id):
	user = await User.find(id)
	return {
		'__template__': 'user.html',
		'__user__': user
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

@post('/api/authenticate')
async def authenticate(*, school_num, passwd):
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
	r.set_cookie(COOKIE_NAME, usertocookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
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

@get('/manage/blogs')
def manage_blogs(*,page='1'):
	return {
		'__template__': 'manage_blogs.html',
		'page_index': get_page_index(page)
	}
	
@get('/manage/blogs/create')
def manage_create_blog():
	return {
		'__template__':'manage_blog_edit.html',
		'id': '',
		'action': '/api/blogs'
	}
	
@get('/manage/blogs/edit')
def manage_edit_blog(*, id):
	return {
		'__template__': 'manage_blog_edit.html',
		'id': id,
		'action': '/api/blogs/%s' % id
	}	
	
@get('/manage/users')
def manage_users(*, page='1'):
	return {
		'__template__': 'manage_users.html',
		'page_index': get_page_index(page)
	}
	
_RE_NUM = re.compile(r'U20[0-1][0-9][0-2][0-9]{4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

@get('/api/users')
async def api_get_users(*,page='1'):
	page_index = get_page_index(page)
	num = await User.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dirt(page=p, users=())
	users = await User.findAll(orderBy='created_at desc', limit=(p.offset,p.limit))
	for u in users:
		u.passwd = '******'
	return dict(page=p, users=users)

@get('/api/users/{id}')
async def api_get_user(*, id):
	user = await User.find(id)
	return user
	
@post('/api/users')
async def api_register_user(*, school_num, name, passwd):
	if not name or not name.strip():
		raise APIValueError('name')
	if not school_num or not _RE_NUM.match(school_num):
		raise APIValueError('school_num')
	if not passwd or not _RE_SHA1.match(passwd):
		raise APIValueError('passwd')
	users = await User.findAll('school_num=?', [school_num])
	if len(users) > 0:
		raise APIError('register:failed', 'school_num', 'School_num is already in use.')
	uid = next_id()
	sha1_passwd = '%s:%s' % (uid, passwd)
	user = User(id=uid, name=name.strip(), school_num=school_num, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
	await user.save()
	# make session cookie:
	r = web.Response()
	r.set_cookie(COOKIE_NAME, usertocookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r
	
@get('/api/blogs')
async def api_blogs(request,*, page='1'):
	check_admin(request)
	page_index = get_page_index(page)
	num = await Blog.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, blogs=())
	blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	return dict(page=p, blogs=blogs)

@get('/api/blogs/{id}')
async def api_get_blog(*, id):
	blog = await Blog.find(id)
	return blog

@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
	check_admin(request)
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty.')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip())
	await blog.save()
	return blog

@post('/api/blogs/{id}')
async def api_update_blog(id, request, *, name, summary, content):
	check_admin(request)
	blog = await Blog.find(id)
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty.')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	blog.name = name.strip()
	blog.summary = summary.strip()
	blog.content = content.strip()
	await blog.update()
	return blog
	
@post('/api/blogs/{id}/delete')
async def api_delete_blog(request, *, id):
	check_admin(request)
	blog = await Blog.find(id)
	await blog.remove()
	return dict(id=id)

@get('/api/comments')
async def api_comments(*, page='1'):
	page_index = get_page_index(page)
	num = await Comment.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, comments=())
	comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	return dict(page=p, comments=comments)

@post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, content):
	user = request.__user__
	if user is None:
		raise APIPermissionError('Please signin first.')
	if not content or not content.strip():
		raise APIValueError('content')
	blog = await Blog.find(id)
	if blog is None:
		raise APIResourceNotFoundError('Blog')
	comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
	await comment.save()
	return comment

@post('/api/comments/{id}/delete')
async def api_delete_comments(id, request):
	check_admin(request)
	c = await Comment.find(id)
	if c is None:
		raise APIResourceNotFoundError('Comment')
	await c.remove()
	return dict(id=id)
	
@get('/api/jobs/{id}')
async def api_jobs(*,id):
	jobs = await Jobs.find(id)
	return jobs

@get('/api/jobs')#debug 删
async def create_jobs():
	f=open('1.md','r',encoding='utf-8')
	title = f.readline()[:-1]
	tim = f.readline()[:-1]
	place = f.readline()[:-1]
	url = f.readline()[:-1]
	content = f.read()
	f.close()
	jobs = Jobs(title=title,tim=tim,place=place,url=url,content=content)
	await jobs.save()
	return jobs