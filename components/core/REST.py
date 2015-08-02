from flask import Flask
from flask import send_file
from flask import request, jsonify, abort, Response, g
from Auth import *
from Models import *
from DownloadManager import *
import json
from multiprocessing import Process
from DownloadDaemon import starter

server = Flask(__name__)
server.config['SECRET_KEY'] = "123456789"
p = None


def token_validator(token):
    user = verify_auth_token(token, server.config['SECRET_KEY'])
    if user != None:
        g.user = user
        token = generate_auth_token(user, server.config['SECRET_KEY'])
        return token
    return None


@server.route('/download/start')
def start():
    token = request.headers['key']
    if str(token)!=server.config['SECRET_KEY']:
        return "{'error':'not authorized'}", 403
    global p
    p = Process(target=starter)
    p.start()
    return "{'status':'" + str(p.pid) + "'}"


@server.route('/download/kill')
def kill():
    token = request.headers['key']
    if str(token)!=server.config['SECRET_KEY']:
        return "{'error':'not authorized'}", 403
    if p is not None:
        p.terminate()
        p.join()
    if not p.is_alive():
        return "{'status':'success'}"
    else:
        return "{'error':'error'}"


@server.route('/api/login', methods=['POST'])
def login():
    userName = request.form['user_name']
    password = request.form['password']
    if user_login(userName, password):
        user = get_user(userName)
        token = generate_auth_token(user, server.config['SECRET_KEY'])
        resp = Response(status=200)
        resp.headers['token'] = token
        return resp
    else:
        abort(403)


@server.route('/api/user', methods=['POST'])
def add_user_request():
    token = token_validator(request.headers['token'])
    if token is not None and g.user.auth == AuthLeval.ADMIN:
        data = request.get_json(force=True)
        try:
            newUser = User(data['user_name'], data['password'], int(data['auth']), data['email'])
            status = add_user(newUser)
            if status == "success":
                resp = Response(response="{'status':'" + status + "'}", status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403


@server.route('/api/user/<string:username>', methods=['DELETE'])
def remove_user_request(username):
    token = token_validator(request.headers['token'])
    if token is not None and g.user.auth == AuthLeval.ADMIN:
        try:
            status = remove_user(username)
            if status == "success":
                resp = Response(response="{'status':'" + status + "'}", status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403


@server.route('/api/user/<string:username>', methods=['PUT'])
def update_user_request(username):
    token = token_validator(request.headers['token'])
    if token is not None and g.user.auth == AuthLeval.ADMIN:
        data = request.get_json(force=True)
        try:
            newUser = User(data['user_name'], data['password'], int(data['auth']), data['email'])
            status = update_user(newUser, username)
            if status == "success":
                resp = Response(response="{'status':'" + status + "'}", status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403


@server.route('/api/user', methods=['GET'])
def get_users_request():
    token = token_validator(request.headers['token'])
    if token is not None and g.user.auth == AuthLeval.ADMIN:
        try:
            status = get_users()
            if not isinstance(status, basestring):
                resp = Response(response=json.dumps(status), status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403


@server.route('/api/user/blocked', methods=['GET'])
def get_blocked_users_request():
    token = token_validator(request.headers['token'])
    if token is not None and g.user.auth == AuthLeval.ADMIN:
        try:
            status = get_blocked_users()
            if not isinstance(status, basestring):
                resp = Response(response=json.dumps(status), status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403


server.route('/api/user/blocked/<string:username>', methods=['POST'])


def block_user_request(username):
    token = token_validator(request.headers['token'])
    if token is not None and g.user.auth == AuthLeval.ADMIN:
        try:
            status = block_user(username)
            if status == "success":
                resp = Response(response="{'status':'" + status + "'}", status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403


server.route('/api/user/blocked/<string:username>', methods=['DELETE'])


def unblock_user_request(username):
    token = token_validator(request.headers['token'])
    if token is not None and g.user.auth == AuthLeval.ADMIN:
        try:
            status = unblock_user(username)
            if status == "success":
                resp = Response(response="{'status':'" + status + "'}", status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403


@server.route('/api/download', methods=['POST'])
def add_download_request():
    token = token_validator(request.headers['token'])
    if token is not None:
        data = request.get_json(force=True)
        try:
            newDownload = Download(data['link'], g.user.userName)
            status = add_download(newDownload)
            if status == "success":
                resp = Response(response="{'status':'" + status + "'}", status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403


@server.route('/api/download/<int:id>', methods=['DELETE'])
def remove_download_request(id):
    token = token_validator(request.headers['token'])
    if token is not None:
        try:
            status = remove_download(id, g.user.userName)
            if status == "success":
                resp = Response(response="{'status':'" + status + "'}", status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403


@server.route('/api/download/rate/<int:id>', methods=['POST'])
def rate_download_request(id):
    token = token_validator(request.headers['token'])
    if token is not None:
        data = request.get_json(force=True)
        try:
            status = rate_download(id, g.user.userName, data['rate'])
            if status == "success":
                resp = Response(response="{'status':'" + status + "'}", status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403


@server.route('/api/user/downloads/<int:limit>', methods=['GET'])
def get_downloads_user_request(limit):
    token = token_validator(request.headers['token'])
    if token is not None :
        try:
            status = get_downloads_user(g.user.userName, int(limit))
            if not isinstance(status, basestring):
                resp = Response(response=json.dumps(status), status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403


@server.route('/api/downloads/<int:limit>', methods=['GET'])
def get_downloads_request(limit):
    token = token_validator(request.headers['token'])
    if token is not None :
        try:
            status = get_downloads(int(limit))
            if not isinstance(status, basestring):
                resp = Response(response=json.dumps(status), status=200)
            else:
                resp = Response(response="{'error':'" + status + "'}", status=400)
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
        resp.headers['token'] = token
        return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403

@server.route('/api/download/<int:id>', methods=['GET'])
def get_download(id):
    token = token_validator(request.headers['token'])
    if token is not None :
        try:
            status = get_download_path(int(id))
            if status is not None and status!="db connection error":
                print status
                return send_file(status,as_attachment=True, mimetype='multipart/form-data')
            else:
                return "{'error':'file not found'}", 404
        except Exception, e:
            resp = Response(response="{'error':'" + e.message + "'}", status=400)
            return resp
    elif token is not None:
        return "{'error':'not authorized'}", 403
    else:
        return "{'error':'token error'}", 403

