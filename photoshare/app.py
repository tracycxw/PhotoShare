######################################
# Chunxi Wang <tracycxw@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
#import flask.ext.login as flask_login
import flask_login
#for image uploading
from werkzeug import secure_filename
import os, base64
import datetime

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1qaz_2wsx' #CHANGE THIS TO YOUR MYSQL PASSWORD
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
TOURIST_EMAIL = 'tourist@bu.edu'

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

def getUsersAlbumPhotos(album_id):
	cursor = conn.cursor()
	# cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	cursor.execute("SELECT imgdata, caption,picture_id FROM Pictures WHERE album_id='{0}'".format(album_id))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getDefaultPic(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata FROM Pictures WHERE picture_id=1")
	row = cursor.fetchall()
	print "!!! getDefaultPic in def"
	print row
	return row

def getUsersProfilePic(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT profilePic FROM Users WHERE user_id = '{0}'".format(uid))
	print uid
	row = cursor.fetchall()
	print "!!! getUsersProfilePic in def "
	print row
	return row

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

def getUserAlbumList(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, album_name, album_date FROM Album WHERE user_id='{0}'".format(uid))
	return cursor.fetchall()

def getUserTags(pid):
	cursor = conn.cursor();
	cursor.execute("SELECT tag_word FROM Tags WHERE picture_id='{0}'".format(pid))
	return cursor.fetchall()

def getAllPhotos():
	cursor = conn.cursor();
	cursor.execute("SELECT picture_id, album_id, imgdata, caption FROM Pictures WHERE picture_id > 1")
	return cursor.fetchall()

def getFriends(uid):
	cursor = conn.cursor();
	cursor.execute("SELECT user_id, email FROM Users U WHERE user_id IN (SELECT friend_id2 from Friends where friend_id1='{0}')".format(uid))
	return cursor.fetchall()

def getNotFriends(uid):
	cursor = conn.cursor();
	cursor.execute("SELECT user_id, email FROM Users U WHERE user_id > 1 and user_id NOT IN (SELECT friend_id2 from Friends where friend_id1='{0}')".format(uid))
	return cursor.fetchall()

def getWholeTags():
	cursor = conn.cursor();
	cursor.execute("SELECT distinct tag_word from Tags")
	return cursor.fetchall()

def getUserWholeTags(uid):
	cursor = conn.cursor();
	cursor.execute("SELECT distinct T.tag_word from Tags T, Pictures P, Album A WHERE A.user_id='{0}' and A.album_id=P.album_id and T.picture_id=P.picture_id".format(uid))
	return cursor.fetchall()

def getUserPhotosByTag(uid, tag_word):
	cursor = conn.cursor();
	cursor.execute("SELECT P.picture_id, P.album_id, P.imgdata, P.caption from Tags T, Pictures P, Album A WHERE A.user_id='{0}' and A.album_id = P.album_id and T.tag_word='{1}' and T.picture_id=P.picture_id".format(uid,tag_word))
	return cursor.fetchall()

def getWholePhotosByTag(tag_word):
	cursor = conn.cursor();
	cursor.execute("SELECT P.picture_id, P.album_id, P.imgdata, P.caption from Tags T, Pictures P WHERE T.tag_word='{0}' and T.picture_id=P.picture_id".format(tag_word))
	return cursor.fetchall()

def getPopularTags():
	cursor = conn.cursor();
	cursor.execute("SELECT tag_word, count(*) from Tags group by tag_word order by count(*) desc limit 5")
	return cursor.fetchall()

def getCommentsByPID(pid):
	cursor = conn.cursor();
	cursor.execute("SELECT comment_id, comment_date, description, picture_id, uid from Comments where picture_id='{0}'".format(pid))
	return cursor.fetchall()

def getPosterUID(pid):
	cursor = conn.cursor();
	cursor.execute("SELECT A.user_id from Album A, Pictures P where A.album_id=P.album_id and P.picture_id='{0}'".format(pid))
	return cursor.fetchone()

def getLikes(pid):
	cursor = conn.cursor();
	cursor.execute("SELECT uid, pid from Likes where pid='{0}'".format(pid))
	return cursor.fetchall()

def hasLiked(uid,pid):
	cursor = conn.cursor();
	cursor.execute("SELECT uid, pid from Likes where uid='{0}' and pid='{1}'".format(uid, pid))
	return cursor.fetchone()

def getCountLikes(pid):
	cursor = conn.cursor();
	cursor.execute("SELECT count(pid) from Likes where pid='{0}'".format(pid))
	return cursor.fetchone()

def getTopTenContributors():
	cursor = conn.cursor();
	cursor.execute("SELECT user_id, uploadContribution, commentContribution, (uploadContribution+commentContribution) as totalContribution from Users where user_id > 1 Order by totalContribution desc Limit 10")
	# cursor.execute("SELECT uid, pic, com, (pic+com) as total From (Select user_id as uid, count(picture_id) as pic from Album natural join Pictures group by user_id)X natural JOIN (Select uid, count(comment_id) as com from Comments group by uid)Y  where uid > 1 Order by total desc Limit 10")
	return cursor.fetchall()

def topFiveTags(uid):
	tagSet = set()
	cursor = conn.cursor()
	cursor.execute("SELECT T.tag_word, count(tag_word) as topFive From Album A, Pictures P, Tags T Where A.user_id = '{0}' and A.album_id=P.album_id and P.picture_id=T.picture_id Group by T.tag_word  Order by topFive desc Limit 5".format(uid))
	for i in cursor:
		tagSet.add(i[0])
	print tagSet
	return tagSet

def getUserWholePic(uid):
	picSet = set()
	cursor = conn.cursor();
	cursor.execute("SELECT P.picture_id from Album A, Pictures P where A.user_id='{0}' and A.album_id=P.album_id".format(uid))
	for i in cursor:
		picSet.add(i[0])
	return picSet


def alsoLikeRecommendation(tagSet,uid, picSet):
	scoreDic = {}
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id, tag_word from Tags")
	for i in cursor:
		print i
		print i[0]
		print i[1]

		if i[1] in tagSet:
			if i[0] not in picSet:
				if scoreDic.has_key(i[0]):
					scoreDic[i[0]] = scoreDic.get(i[0]) + 1
				else:
					scoreDic[i[0]] = 1
		else:
			if i[0] not in picSet:
				if scoreDic.has_key(i[0]):
					scoreDic[i[0]] = scoreDic.get(i[0]) - 0.001
				else:
					scoreDic[i[0]] = - 0.001
	print "score dic"
	print scoreDic
	res = sorted(scoreDic.items(), key=lambda x: (-x[1], x[0]))
	print res
	return res

def getPhotoByPID(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id, album_id, imgdata, caption from Pictures where picture_id='{0}';".format(pid))
	return cursor.fetchall()

def getPIDByTag(tag_word):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id from Tags where tag_word='{0}'".format(tag_word))
	return cursor.fetchall()

def getTagByPID(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_word from Tags where picture_id='{0}'".format(pid))
	return cursor.fetchall()

def hasFollowed(uid,email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	user = cursor.fetchone()[0]
	print "!!! user"
	print user
	print cursor.execute("SELECT * From Friends where friend_id1='{0}' and friend_id2='{1}'".format(uid, user))
	if cursor.execute("SELECT * From Friends where friend_id1='{0}' and friend_id2='{1}'".format(uid, user)):
		# true means already exists this friendship
		return True
	else:
		return False

def getUserByUID(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, email  FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()


#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#================================================
@app.route("/", methods=['GET'])
def homepage():
	return render_template('homepage.html', message='Welcome to Photoshare')

@app.route('/signinpage', methods=['GET', 'POST'])
def signinpage():
	if flask.request.method == 'GET':
		return '''
			   <form action='signinpage' method='POST'>
			   	<h4>This is Log in Page</h4>
				Email: <input type='text' name='email' id='email' placeholder='email'></input></br>
				Password: <input type='password' name='password' id='password' placeholder='password'></input></br>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Back</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('profilepage')) #protected is a function defined in this file
	#information did not match
	return "<a href='/signinpage'>Try again</a>\
			</br><a href='/signuppage'>or make an account</a>"

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/signuppage/", methods=['GET'])
def signuppage():
	return render_template('improved_signuppage.html', message='This is sign up page!',supress=True)  

@app.route("/signuppage/", methods=['POST'])
def signup_user():
	try:
		email=request.form.get('email')
                print email
		password=request.form.get('password')
		firstName = request.form.get('firstName')
		lastName = request.form.get('lastName')
		birth = request.form.get('birthday')
		# imgfile = request.files['photo']
		profilePic = request.form.get('photo')
		print "first"
		print profilePic
		bio = request.form.get('bio')
		hometown = request.form.get('hometown')
		gender = request.form.get('gender')
	except:
		print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
		#information did not match
		return render_template('improved_signuppage.html', message='some information is missing!')
	imgfile = None
	try: 
		imgfile = request.files['photo']
	except:
		print "no imgfile"
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		try:
			print "try email"
			print email
			print "imgfile"
			print imgfile
			if imgfile != None:
				profilePic = base64.standard_b64encode(imgfile.read())
			else:
				cursor.execute("SELECT imgdata from Pictures where album_id=1")
				profilePic = cursor.fetchone()[0]
			print "success in profilePic"
			print cursor.execute("INSERT INTO Users (email, password, firstName, lastName, birth, profilePic, bio, hometown, gender, uploadContribution, commentContribution) VALUES ('{0}', '{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}')".format(email, password, firstName, lastName, birth, profilePic, bio, hometown, gender, 0, 0))			
			conn.commit()
			user = User()
			user.id = email
			flask_login.login_user(user)
			uid = getUserIdFromEmail(email)
			cursor.execute("INSERT INTO Friends(friend_id1, friend_id2) VALUES ('{0}','{1}')".format(uid, uid))
			return flask.redirect(flask.url_for('profilepage', name=email, message='Account Created!'))
		except:
			return "<a href='/signuppage'>Try again, some information is missiong</a></br>"
	else:
		print "couldn't find all tokens"
		#information did not match
		return "<a href='/signuppage'>Try again, this email has existed</a></br>"

@app.route('/logoutpage')
def logoutpage():
	flask_login.logout_user()
	return render_template('homepage.html', message='Logged out') 

@app.route('/profilepage', methods=['GET', 'POST'])
@flask_login.login_required
def profilepage():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		# caption = request.form.get('caption')
		# print caption
		photo_data = base64.standard_b64encode(imgfile.read())
		print "!!! current photo_data"
		print photo_data
		cursor = conn.cursor()
		if flask_login.current_user.id == TOURIST_EMAIL:
			"!!! update default picture in "
			print cursor.execute("UPDATE Pictures SET imgdata='{0}' where picture_id=1".format(photo_data))
		print "!!! update user profile picture"
		print cursor.execute("UPDATE Users SET profilePic='{0}' where email='{1}'".format(photo_data,flask_login.current_user.id))
		conn.commit()
		print "!!! imagedata"
		print "!!! getDefaultPic in profilepage"
		print getDefaultPic(uid)
		print "!!! getUsersProfilePic in profilepage"
		temp = getUsersProfilePic(uid)
		print temp
		return render_template('profilepage.html', name=flask_login.current_user.id, message="Here's your profile page", photos=getUsersProfilePic(uid))
	
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		print "!!! page get"
		uid = getUserIdFromEmail(flask_login.current_user.id)
		print getUsersProfilePic(uid)
		print 'uid is ' + str(uid)
		pic = getUsersProfilePic(uid)
		print "!! pic"
		if pic[0][0]=='None':
			pic = getDefaultPic(uid)
		print "!!! pic now"
		print pic
		return render_template('profilepage.html',name=flask_login.current_user.id, message="Here's your profile", photos=pic)
#end photo uploading code 

@app.route('/createAlbum', methods=['GET', 'POST'])
@flask_login.login_required
def create_album_page():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		# imgfile = request.files['photo']
		album_name = request.form.get('album_name')
		album_date = request.form.get('album_date')
		print album_name
		print album_date
		# photo_data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Album (album_name, user_id, album_date) VALUES ('{0}', '{1}', '{2}' )".format(album_name,uid, album_date))
		conn.commit()

		temp = getUserAlbumList(uid)
		print "!!! this is create_album_page"
		print temp
		# return flask.redirect(flask.url_for('albums', name=flask_login.current_user.id, a_name= album_name,message='Album created!'))
		return render_template('albums.html', name=flask_login.current_user.id, a_name= album_name,createmessage='Album created!')
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('createAlbum.html')
#end photo uploading code 

@app.route('/curAlbum/<album_name>/<album_id>', methods=['GET', 'POST'])
@flask_login.login_required
def cur_album_page(album_name,album_id): 
	if request.method == 'GET':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		print uid
		print "!!! album_name"
		print album_name
		print "!!! album_id"
		print album_id
		return render_template('curAlbum.html', name=uid, a_name=album_name, aid =album_id,photos=getUsersAlbumPhotos(album_id))
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		print caption
		photo_data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		print "album_id"
		print album_id
		print "album_name"
		print album_name
		cursor.execute("INSERT INTO Pictures (album_id, imgdata, caption) VALUES ('{0}', '{1}', '{2}' )".format(album_id, photo_data, caption))
		cursor.execute("UPDATE Users SET uploadContribution= uploadContribution+1 where user_id='{0}'".format(uid))
		conn.commit()
		return render_template('curAlbum.html', name=uid, a_name=album_name, aid=album_id, photos=getUsersAlbumPhotos(album_id))

@app.route('/albums', methods=['GET', 'POST'])
@flask_login.login_required
def albums():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	album_list = getUserAlbumList(uid)
	print "!!! albums in albums"
	print album_list
	return render_template('albums.html',name=uid, message='This is your albums', albums = getUserAlbumList(uid))

@app.route('/delete_photo/<a_name>/<a_id>/<p_id>', methods=['GET', 'POST'])
@flask_login.login_required
def delete_photo(a_name, a_id, p_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Pictures where picture_id='{0}'".format(p_id))
	conn.commit()	
	return render_template('curAlbum.html', name=uid, a_name=a_name, aid=a_id, photos=getUsersAlbumPhotos(a_id))

#delete_album
@app.route('/delete_album/<album_id>', methods=['GET', 'POST'])
@flask_login.login_required
def delete_album(album_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Album where album_id='{0}'".format(album_id))
	conn.commit()
	album_list = getUserAlbumList(uid)
	print "!!! albums in delete_album"
	print album_list
	return render_template('albums.html',name=uid, message='Album created!', albums = getUserAlbumList(uid))

@app.route('/view_tags/<a_name>/<aid>/<pid>', methods=['GET', 'POST'])
@flask_login.login_required
def view_tags(a_name, aid, pid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'GET':
		tags = getUserTags(pid)
		print "tags in view_tags"
		print tags
		return render_template('viewtags.html',name=uid, a_name=a_name, aid=aid, tags=tags, pid=pid)
	else:
		if request.form.get('deleteTag') is not None:
			curTag = request.form.get('deleteTag')
			print "!! curTag"
			print curTag
			cursor = conn.cursor()
			print cursor.execute("DELETE FROM Tags WHERE picture_id = '{0}' and tag_word='{1}'".format(pid,curTag))
			conn.commit()
			# return render_template('viewtags.html',name=uid, a_name=a_name, aid=aid, tags=getUserTags(pid), pid=pid)
		else:
			try:
				newtag=request.form.get('tag')
				print "!!! newtag in view_tags"
				print newtag
				print pid
				cursor = conn.cursor()
				print cursor.execute("INSERT INTO Tags (picture_id, tag_word) VALUES ('{0}','{1}')".format(pid,newtag))
				conn.commit()
				# return render_template('viewtags.html',name=uid, a_name=a_name, aid=aid, tags=getUserTags(pid), pid=pid)
			except:
				print "error"
		return render_template('viewtags.html',name=uid, a_name=a_name, aid=aid, tags=getUserTags(pid), pid=pid)

@app.route('/delete_tag/<a_name>/<aid>/<pid>', methods=['GET', 'POST'])
@flask_login.login_required
def delete_tag(a_name, aid, pid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Tags (picture_id, tag_word) VALUES ('{0}','{1}')".format(pid,newtag))
	conn.commit()
	return render_template('viewtags.html',name=uid, a_name=a_name, aid=aid, tags=getUserTags(pid), pid=pid)

@app.route('/searchFriends/<flag>', methods=['GET', 'POST'])
@flask_login.login_required
def searchFriends(flag):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	# flag = 1: search friends, flag=0 show friends
	print "!!!"
	print flag
	print flag == '1'
	if request.method == 'GET':
		friends = None
		if (flag == '1'):
			friends = getNotFriends(uid)
			print "flag1 friends search"
			print friends
			return render_template('searchFriends.html',name=flask_login.current_user.id, message='Here you can add friends',  friends=friends)
		else:
			friends = getFriends(uid)
			print "flag0 friends view"
			print friends
			return render_template('viewFriends.html',name=flask_login.current_user.id, message='Here are your friends',friends=friends)
	else:
		# friends = getNotFriends(uid)
		if request.form.get('addFriend') is not None:
			friend_id2 = request.form.get('addFriend')
			cursor = conn.cursor()
			print cursor.execute("INSERT INTO Friends (friend_id1, friend_id2) VALUES ('{0}','{1}')".format(uid,friend_id2))
			conn.commit()
			friends = getNotFriends(uid)
			return render_template('searchFriends.html',name=flask_login.current_user.id, message='Here you can add friends',flag=flag, friends=friends)
		if request.form.get('search') is not None:
			if request.form.get('searchFriends') is not None:
				curFriendEmail = request.form.get('searchFriends')
				print "!!! curFriendEmail"
				print curFriendEmail
				if isEmailUnique(curFriendEmail):
					friends = getNotFriends(uid)
					return render_template('searchFriends.html',name=flask_login.current_user.id, message='friend not exists',flag=flag, friends=friends)

				if hasFollowed(uid, curFriendEmail) == False:
					cursor = conn.cursor()
					cursor.execute("SELECT user_id, email  FROM Users WHERE email = '{0}'".format(curFriendEmail))
					friendid = cursor.fetchone()[0]
					print "!!! start search"
					friends = getUserByUID(friendid)

					return render_template('searchFriends.html',name=flask_login.current_user.id, message='successful search',flag=flag, friends=friends)
				else:
					friends = getNotFriends(uid)
					return render_template('searchFriends.html',name=flask_login.current_user.id, message='already add this friend',flag=flag, friends=friends)
			else:
				friends = getNotFriends(uid)
				return render_template('searchFriends.html',name=flask_login.current_user.id, message='Here you can add friends',flag=flag, friends=friends)
		else:
			print "not implement"

@app.route('/tagAlbums', methods=['GET', 'POST'])
@flask_login.login_required
def tagAlbums():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		if request.form.get('showphotos') is not None:
			print "clicked btn show photos"
			tag_word = request.form.get('showphotos') 
			print "tag_word"
			print tag_word
			photos = getUserPhotosByTag(uid, tag_word)
			print photos
			return render_template('tagAlbums.html', name=flask_login.current_user.id, message="Here are the photos",photos=photos)
		else:
			tags = getUserWholeTags(uid)
			print "whole tags 1"
			print tags
			return render_template('tagAlbums.html',name=flask_login.current_user.id, message='Here is all your tags', tags=tags)
	else:
		tags = getUserWholeTags(uid)
		print "whole tags 2"
		print tags
		return render_template('tagAlbums.html',name=flask_login.current_user.id, message='Here is all your tags', tags=tags)

@app.route('/wholeTagAlbums', methods=['GET', 'POST'])
@flask_login.login_required
def wholeTagAlbums():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		if request.form.get('showphotos') is not None:
			print "clicked btn show photos"
			tag_word = request.form.get('showphotos') 
			print "tag_word"
			print tag_word
			photos = getWholePhotosByTag(tag_word)
			print photos
			return render_template('wholeTagAlbums.html', name=uid, message="view photos by tag",photos=photos)
		else:
			tags = getWholeTags()
			print "whole tags 1"
			print tags
			return render_template('wholeTagAlbums.html',name=uid, message='Here is all your tags', tags=tags)
	else:
		tags = getWholeTags()
		print "whole tags of the website"
		print tags
		return render_template('wholeTagAlbums.html',name=uid, message='Here is all tags in website', tags=tags)

#popularTagAlbums
@app.route('/popularTagAlbums', methods=['GET', 'POST'])
@flask_login.login_required
def popularTagAlbums():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		print "not implement"
	else:
		tags = getPopularTags()
		return render_template('wholeTagAlbums.html',name=uid, message='Here is most 5 popular tags in website', tags=tags)

#view_comments
@app.route('/viewComments/<pid>', methods=['GET', 'POST'])
@flask_login.login_required
def viewComments(pid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	poster = getPosterUID(pid)[0]
	print "!!! poster"
	print poster == uid
	flag = poster==uid
	if request.method =='POST':
		if request.form.get('commentBtn') is not None:
			try:
				commentText = request.form.get('commentBox')
				print "commentBox"
				print commentText
				if commentText == '':
					comments = getCommentsByPID(pid)
					return render_template('viewComments.html',name=uid, comments=comments, pid=pid, flag=flag)
				commentDate = datetime.datetime.today().strftime('%Y-%m-%d')
				print commentDate
				cursor = conn.cursor()
				print cursor.execute("INSERT INTO Comments (comment_date, description, picture_id, uid) VALUES ('{0}','{1}','{2}','{3}')".format(commentDate,commentText,pid,uid))
				cursor.execute("UPDATE Users SET commentContribution=commentContribution+1 where user_id='{0}'".format(uid))
				conn.commit()
			except:
				print "empty comment"
	comments = getCommentsByPID(pid)
	return render_template('viewComments.html',name=uid, comments=comments, pid=pid, flag=flag)


@app.route('/viewLike/<pid>', methods=['GET', 'POST'])
@flask_login.login_required
def viewLike(pid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	# has liked this photo: flag=1, otherwise flag=0
	print "has liked?"
	print hasLiked(uid,pid)
	message = None
	if request.method == 'POST':
		if request.form.get('likeBtn') is not None:
			# if hasLiked(uid,pid) == None:
			if uid == 1:
				message = "tourists are not allowed to like photo"
			else:
				try:
					cursor = conn.cursor()
					print cursor.execute("INSERT INTO Likes (uid, pid) VALUES ('{0}','{1}')".format(uid,pid))
					conn.commit()
				except:
					message = "has already liked it"
	likes = getLikes(pid)
	countLikes = getCountLikes(pid)
	return render_template('viewLike.html',name=uid, likes=likes, countLikes=countLikes, pid=pid, message=message)

@app.route('/contribution', methods=['GET', 'POST'])
@flask_login.login_required
def contribution():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	topten = getTopTenContributors()
	return render_template('contribution.html', topten=topten)


@app.route('/youMayAlsoLike', methods=['GET', 'POST'])
@flask_login.login_required
def youMayAlsoLike():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	tagSet = topFiveTags(uid)
	picSet = getUserWholePic(uid)
	res = alsoLikeRecommendation(tagSet,uid,picSet)
	photos = ()
	for i in res:
		print "!!! ddd"
		print i[0]
		photos = photos + getPhotoByPID(i[0])	
	print photos
	return render_template('tagAlbums.html',name=flask_login.current_user.id, message='you may also like these photos', photos=photos)

#tagRecommendation
@app.route('/tagRecommendation', methods=['GET', 'POST'])
@flask_login.login_required
def tagRecommendation():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		if request.form.get('search') is not None:
			tagString = request.form.get('searchTag')
			tagList = tagString.split()
			print "tagList"
			print tagList
			pidSet = set()
			
			for i in range(len(tagList)):
				temp = getPIDByTag(tagList[i])
				for j in temp:
					pidSet.add(j[0])
			print pidSet
			newTagDic = {}
			for i in pidSet:
				temp = getTagByPID(i)
				for j in temp:
					if j[0] not in tagList: # if not in, add into dic
						if newTagDic.has_key(j[0]): # if dic has this key then count+1
							newTagDic[j[0]] = newTagDic.get(j[0]) + 1
						else:
							newTagDic[j[0]] = 1
			print "newTagDic"
			print newTagDic
			res = sorted(newTagDic.items(), key=lambda x: (-x[1], x[0]))
			print res			
			return render_template('tagRecommendation.html',name=flask_login.current_user.id,tags = res)
		if request.form.get('showphotos') is not None:
			curtag = request.form.get('showphotos')
			photos = getWholePhotosByTag(curtag)
			return render_template('viewRecTagPic.html',name=flask_login.current_user.id,message='recommend to you all photos with this tag in the website',photos=photos)
	return render_template('tagRecommendation.html',name=flask_login.current_user.id)


@app.route('/welcomepage', methods=['GET', 'POST'])
# @flask_login.login_required
def welcomepage():
	print "!!!cur user"
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		if request.form.get('search') is not None:
			try:
				if request.form.get('searchTag') == '' :
					print "empty search"
					return render_template('welcomepage.html',name=uid, message='Welcome!', photos=getAllPhotos())
				else:
					tagString = request.form.get('searchTag')
					print "!!! tagString here"
					print tagString
					tagList = tagString.split()
					print "!!! tagList here"
					print tagList

					pidList = []
					for i in range(len(tagList)):
						print "!!! cur pid"
						print getPIDByTag(tagList[i])
						curpids = getPIDByTag(tagList[i])
						temp = []
						for j in curpids:
							print j
							temp.append(j[0])
						pidList.append(temp)
						# pidList.append(getPIDByTag(tagList[i]))
					pidSet = set(pidList[0]).intersection(*pidList)
					print "!!! pidSet"
					print pidSet

					picFiltered = list(pidSet)
					print picFiltered
					photos = ()
					if picFiltered != []:
						print "in loop" 
						for i in picFiltered:
							photos += getPhotoByPID(i)
					return render_template('welcomepage.html',name=uid, message='Welcome!', photos=photos)
			except:
				print 'empty search tag'
				return render_template('welcomepage.html',name=uid, message='Welcome!', photos=getAllPhotos())
	else:
		return render_template('welcomepage.html',name=uid, message='Welcome!', photos=getAllPhotos())


@app.route('/tourist', methods=['GET', 'POST'])
def tourist():
	email = TOURIST_EMAIL
	pwd = 'test'
	user = User()
	user.id = email
	flask_login.login_user(user)
	uid = 1
	return flask.redirect(flask.url_for('welcomepage')) 



if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)
