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
spoonacular_API_KEY = os.getenv("SPOONACULAR_API_KEY")

DEX_TOKEN_URL = 'http://dex:5556/token'
DEX_USERINFO_URL = 'http://dex:5556/userinfo'


app = Flask(__name__, static_folder='dist', static_url_path='')
CORS(app, supports_credentials=True, resources={r"/*": {"origins": frontend_url}})
app.secret_key = os.getenv("SECRET_KEY")
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

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
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    email = user['email']
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT goal_type, starting_weight, latest_weight, target_weight, 
               duration_days, start_date 
        FROM goals 
        WHERE email = ?
    """, (email,))
    row = cursor.fetchone()
    cnx.close()
    
    if not row:
        return jsonify({"error": "No goal found"}), 404
        
    return jsonify({
        "goal_type": row["goal_type"],
        "starting_weight": row["starting_weight"],
        "latest_weight": row["latest_weight"],
        "target_weight": row["target_weight"],
        "duration_days": row["duration_days"],
        "start_date": row["start_date"]
    })

@app.route('/goal', methods=['POST'])
def set_goal():
    user = session.get('user')
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
        
    email = user['email']
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['goal_type', 'starting_weight', 'latest_weight', 
                      'target_weight', 'duration_days', 'start_date']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    cnx = get_db_connection()
    cursor = cnx.cursor()
    
    # Calculate calories suggestion
    weight_diff = data['target_weight'] - data['starting_weight']
    calories_need = weight_diff * 7700
    calories_sug = round(calories_need / data['duration_days'])
    
    cursor.execute("""
        INSERT INTO goals (
            email, goal_type, starting_weight, latest_weight, 
            target_weight, duration_days, start_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            goal_type = excluded.goal_type,
            starting_weight = excluded.starting_weight,
            latest_weight = excluded.latest_weight,
            target_weight = excluded.target_weight,
            duration_days = excluded.duration_days,
            start_date = excluded.start_date
    """, (
        email,
        data['goal_type'],
        data['starting_weight'],
        data['latest_weight'],
        data['target_weight'],
        data['duration_days'],
        data['start_date']
    ))
    
    cnx.commit()
    cnx.close()

    return jsonify({
        'message': 'Goal saved successfully!',
        'calories_sug': calories_sug
    })

@app.route('/goal', methods=['DELETE'])
def delete_goal():
    user = session.get('user')
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
        
    email = user['email']
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("DELETE FROM goals WHERE email = ?", (email,))
    cnx.commit()
    cnx.close()
    
    return jsonify({"message": "Goal deleted successfully"})

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

@app.route('/api/recipe', methods=['GET'])
def get_recipe():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Missing food query"}), 400
    
    api_url = 'https://api.spoonacular.com/recipes/complexSearch'
    
    params = {
        'query': query,
        'apiKey': spoonacular_API_KEY,
        'number': 10,
        'addRecipeInformation': True,
        'fillIngredients': True,
        'addRecipeInstructions': True,
    }
    
    try:
        res = requests.get(api_url, params=params)
        
        if res.status_code == 200:
            data = res.json()
            recipes = data.get('results', [])
            
            items = []
            for recipe in recipes:
                # Extract ingredients
                ingredients = []
                for ing in recipe.get('extendedIngredients', []):
                    amount = ing.get('amount', '')
                    unit = ing.get('unit', '')
                    name = ing.get('name', '')
                    ingredients.append(f"{amount} {unit} {name}".strip())
                
                # Extract instructions
                instructions = []
                for instruction_group in recipe.get('analyzedInstructions', []):
                    for step in instruction_group.get('steps', []):
                        instructions.append(step.get('step', ''))
                
                item = {
                    'title': recipe.get('title', ''),
                    'ingredients': '|'.join(ingredients),
                    'instructions': '. '.join(instructions),
                    'servings': str(recipe.get('servings', '')),
                    'image': recipe.get('image', '')
                }
                items.append(item)
            
            return jsonify({"items": items})
        else:
            return jsonify({
                "error": "Failed to fetch recipes",
                "status": res.status_code,
                "message": res.text
            }), res.status_code
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# add recipe to favorites
@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    user = session.get('user')
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
        
    email = user['email']
    data = request.get_json()
    recipe = data['recipe']

    cnx = get_db_connection()
    cursor = cnx.cursor()

    # Check if already exists
    cursor.execute(
        "SELECT 1 FROM favorite_recipes WHERE email = ? AND recipe_title = ?", 
        (email, recipe)
    )
    cursor.execute("""
        INSERT INTO favorite_recipes (email, recipe_title) VALUES (?, ?)""", 
    (email, recipe))

    cnx.commit()
    cnx.close()

    return jsonify({
        'sucess': True
    })

# get user's favorite recipes
@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    user = session.get('user')
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
        
    email = user['email']

    cnx = get_db_connection()
    cursor = cnx.cursor()

    cursor.execute(
        """SELECT recipe_title FROM favorite_recipes WHERE email = ?""",
        (email,)
    )

    favorites = [row['recipe_title'] for row in cursor.fetchall()]
    cnx.close()

    return jsonify({'favorites': favorites})

# remove recipe from user's favorites
@app.route('/api/favorites', methods=['DELETE'])
def remove_favorite():

    user = session.get('user')
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
        
    email = user['email']
    data = request.get_json()
    recipe = data['recipe']

    if not email or not recipe:
        return jsonify({'error': 'Missing email or recipe'}), 400

    cnx = get_db_connection()
    cursor = cnx.cursor()

    try:
        cursor.execute(
            """DELETE FROM favorite_recipes WHERE email = ? AND recipe_title = ?""",
            (email, recipe)
        )
        cnx.commit()
        cnx.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8000)
