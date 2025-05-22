from flask import Flask, send_from_directory, request, redirect, session
import os
import secrets
import requests

clientSecret = os.getenv("OIDC_CLIENT_SECRET")
clientID = os.getenv("OIDC_CLIENT_ID")
reDirect = 'http://localhost:8000/auth/callback'
frontend_url = os.getenv("FRONTEND_URL")

DEX_TOKEN_URL = 'http://dex:5556/token'
DEX_USERINFO_URL = 'http://dex:5556/userinfo'

app = Flask(__name__, static_folder='dist', static_url_path='')
app.secret_key = secrets.token_hex(16)
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def catch_all(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Let Svelte SPA router handle it
        return send_from_directory(app.static_folder, 'index.html')

@app.route("/auth/callback")
def auth_callback():
    try:
        #check if code returned by Dex (to exchange for access token)
        code = request.args.get("code")
        if not code:
            return "Missing Code", 400
        #token request call to dex; parameters sourced from Dex documentation
        token_resp = requests.post(DEX_TOKEN_URL, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': reDirect,
            'client_id': clientID,
            'client_secret': clientSecret
        }, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        #Check if token request was successful
        if token_resp.status_code != 200:
            app.logger.error(f"Token response error: {token_resp.text}")
            return f"Failed to get token: {token_resp.text}", 500

        token_data = token_resp.json()
        access_token = token_data.get('access_token')
        #check if the token response contains access_token
        if not access_token:
            return "No access token received", 500

        userinfo_resp = requests.get(DEX_USERINFO_URL, headers={
            'Authorization': f'Bearer {access_token}'
        })
        #check if getting userinfo was successful 
        if userinfo_resp.status_code != 200:
            app.logger.error(f"Userinfo response error: {userinfo_resp.text}")
            return f"Failed to get user info: {userinfo_resp.text}", 500
        #store it in flask
        userinfo = userinfo_resp.json()
        session['user'] = userinfo

        return redirect(frontend_url)
    except Exception as e:
        app.logger.exception("Error in /auth/callback")
        return f"error in callback", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
