from datetime import datetime, timedelta
from urllib import response
from flask import Flask, jsonify, redirect, request, session
from flask_cors import CORS, cross_origin
import requests

import urllib.parse

app = Flask(__name__)
app.secret_key = 'super_secret_key'
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])  # Enable CORS globally with support for credentials  ,origins=["http://127.0.0.1:8080", "http://127.0.0.1:5173"],

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['SESSION_COOKIE_NAME'] = 'my_session_cookie'
app.config['SESSION_COOKIE_DOMAIN'] = '.localhost'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # or 'None' if using HTTPS




CLIENT_ID  = "5421c67558764234b64af44be192c28b"
CLIENT_SECRET  = "278868ae7b67444ba0d9de8e9ea50b2d"
REDIRECT_URI  = "http://localhost:8080/callback"

AUTH_URL  = "https://accounts.spotify.com/authorize"
TOKEN_URL  = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

@app.route('/')
def index():
    return "Welcome to my Spotify App <a href='/login'>Login with Spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'
    params = {
        'client_id':CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error":request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri':REDIRECT_URI,
            'client_id':CLIENT_ID,
            'client_secret':CLIENT_SECRET
        }
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] =datetime.now().timestamp() + token_info['expires_in']

        print("Access Token print line 61: "+session['access_token'])

        #return redirect('/playlists')
        #return redirect('http://127.0.0.1:5173/dashboard')
    return redirect('http://localhost:5173/dashboard')

@app.route('/playlists')
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'], supports_credentials=True)
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists = response.json()

    return jsonify(playlists)

@app.route('/hello-world')
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'], supports_credentials=True)
def hello_world():
    return "Hello World"

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type':'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id':CLIENT_ID,
            'client_secret':CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] =datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/playlists')

if __name__== '__main__':
    app.run(host='localhost', port=8080, debug=True)