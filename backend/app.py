from flask import Flask, send_from_directory, request, redirect, session, jsonify
from flask_cors import CORS
import os
import secrets
import requests

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

        return redirect(frontend_url)
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

#Logout redirection
@app.route("/logout")
def logout():
    session.clear()
    response = redirect(frontend_url)
    response.set_cookie('session', '', expires=0)
    return response
    
#login page 
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get('email') == 'test@example.com' and data.get('password') == '123456':
        return jsonify({"message": "Login successful", "token": "dummy-jwt-token"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    return jsonify({"message": "Registration successful"}), 201

#Calculator Page
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    weight = data.get('weight')
    height = data.get('height')
    age = data.get('age')
    sex = data.get('sex')
    activity = data.get('activity')  # 1.2 ~ 1.9

    if sex == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    tdee = bmr * activity

    #macro
    carbs_ratio = 0.50
    protein_ratio = 0.20
    fat_ratio = 0.30

    # calculate calorie
    carbs_g = round((tdee * carbs_ratio) / 4)
    protein_g = round((tdee * protein_ratio) / 4)
    fat_g = round((tdee * fat_ratio) / 9)

    # database?

    return jsonify({
        "bmr": round(bmr, 2),
        "tdee": round(tdee, 2),
        "macros": {
            "carbs_g": carbs_g,
            "protein_g": protein_g,
            "fat_g": fat_g
        }
    })


#Goal Page
@app.route('/goal', methods=['POST'])
def set_goal():
    data = request.json
    goal_type = data.get('goal_type')  # lose, maintain, gain?
    target_weight = data.get('target_weight')
    duration_days = data.get('duration_days')

    calorie_adjust = 500 if goal_type == "lose" else (-500 if goal_type == "gain" else 0)

    return jsonify({
        "message": "goal set successfully",
        "calorie_adjust": calorie_adjust
    })

#Planner Page
@app.route('/plan', methods=['POST'])
def generate_plan():
    data = request.json
    meals = data.get('meals')  # 

    return jsonify({
        "suggestion": {
            "breakfast": "",
            "lunch": "",
            "dinner": ""
        }
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
            {"name": "Oatmeal Banana Pancakes", "calories": 350},
            {"name": "Tuna Salad Wrap", "calories": 420},
            {"name": "Tofu Stir-Fry", "calories": 500}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
