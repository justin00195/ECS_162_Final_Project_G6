from flask import Flask, send_from_directory, request, redirect, session, jsonify
from flask_cors import CORS
import os
import secrets
import requests
from db import get_db_connection

clientSecret = os.getenv("OIDC_CLIENT_SECRET")
clientID = os.getenv("OIDC_CLIENT_ID")
reDirect = 'http://localhost:8000/auth/callback'
frontend_url = os.getenv("FRONTEND_URL")
cal_api_key = os.getenv("CAL_NJ_API_KEY")

DEX_TOKEN_URL = 'http://dex:5556/token'
DEX_USERINFO_URL = 'http://dex:5556/userinfo'


app = Flask(__name__, static_folder='dist', static_url_path='')
CORS(app, supports_credentials=True, resources={r"/*": {"origins": frontend_url}})
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
        return redirect(f"{frontend_url}#/user-portal")
    except Exception as e:
        app.logger.exception("Error in /auth/callback")
        return f"error in callback", 500
    
    #Used for getting user info to make sure that the login was successful
@app.route("/auth/user")
def get_logged_in_user():
    user = session.get('user')
    app.logger.debug(f"Session user: {user}")  # Log the session state

    # Explicitly check if the session is empty and return 401 if no user is logged in
    #use this for unit testing
    if user is None:
        app.logger.debug("No user found in session.")
        return jsonify({"user": None}), 401
    return jsonify(user)

#user profile
@app.route('/user/profile', methods=['GET'])
def get_profile():
    user = session.get('user')
    email = user['email']
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,)) #reference: https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html
    row = cursor.fetchone() # reference: https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-fetchone.html
    cnx.close()
    # reference: https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor.html
    return jsonify({
        "name": row["name"],
        "gender": row["gender"],
        "age": row["age"],
        "height": row["height"],
        "weight": row["weight"],
        "activity_level": row["activity_level"]
    })


@app.route('/user/profile', methods=['POST'])
def save_profile():
    user = session.get('user')
    email = user.get('email')
    data = request.json
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("""
        INSERT INTO users (email, name, gender, age, height, weight, activity_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            name=excluded.name,
            gender=excluded.gender,
            age=excluded.age,
            height=excluded.height,
            weight=excluded.weight,
            activity_level=excluded.activity_level
    """, (
        email,
        data.get("name"),
        data.get("gender"),
        data.get("age"),
        data.get("height"),
        data.get("weight"),
        data.get("activity_level")
    ))
    cnx.commit()
    cnx.close()
    return jsonify({"message": "Profile saved"})



#Calculator Page
@app.route('/calculate', methods=['GET'])
def calculate():
    user = session.get('user')
    email = user['email']
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    profile = cursor.fetchone()
    cnx.close()
    weight = profile['weight']
    height = profile['height']
    age = profile['age']
    sex = profile['gender']
    activity = profile['activity_level']
    if sex == 'male':
        bmr = 88.362 + 13.397 * weight + 4.799 * height - 5.677 * age 
    else:
        bmr = 447.593 + 9.247 * weight + 3.098  * height - 54.330 * age 

    tdee = bmr * activity
    return jsonify({
        "bmr": round(bmr),
        "tdee": round(tdee)
    })

#Goal Page
@app.route('/goal', methods=['GET'])
def get_goal():
    user = session.get('user')
    email = user['email']
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT target_weight, duration_days FROM goals WHERE email = ?", (email,))
    row = cursor.fetchone()
    cnx.close()
    return jsonify({
        "target_weight": row["target_weight"],
        "duration_days": row["duration_days"]
    })

@app.route("/logout")
def logout():
    session.clear()
    response = redirect(frontend_url)
    response.set_cookie('session', '', expires=0)
    return response

@app.route('/goal', methods=['POST'])
def set_goal():
    user = session.get('user')
    email = user['email']
    data = request.get_json()
    target_weight = data.get('target_weight')
    duration_days = data.get('duration_days')
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT weight FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    current_weight = row['weight']

    # calculate calories suggestion
    weight_diff = target_weight - current_weight
    calories_need = weight_diff * 7700
    calories_sug = round(calories_need / duration_days)
    cursor.execute("""
        INSERT INTO goals (email, target_weight, duration_days)
        VALUES (?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            target_weight=excluded.target_weight,
            duration_days=excluded.duration_days
    """, (email, target_weight, duration_days))
    cnx.commit()
    cnx.close()

    return jsonify({
        'message': 'Goal saved successfully!',
        'calories_sug': calories_sug
    })

#Report Page
@app.route('/report', methods=['POST'])
def report():
  data = request.json
  query = data.get('query')
  
  if not query:
      return jsonify({"error": "Missing food query"}), 400
  
  api_url = f'https://api.calorieninjas.com/v1/nutrition?query={query}'
  response = requests.get(api_url, headers={'X-Api-key': cal_api_key})
  if response.status_code == 200:
      return jsonify(response.json())
  else:
      return jsonify({"error": "FAILED TO GET FOOD DATA"})

#Recipe Page
@app.route('/recipes', methods=['GET'])
def get_recipes():
    return jsonify({
        "recipes": [
            {"name": "egg", "calories": 100},
            {"name": "steak", "calories": 400},
            {"name": "chicken", "calories": 500} #should we implement from api?
        ]
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8000)
