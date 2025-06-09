from flask import Flask, send_from_directory, request, redirect, session, jsonify
from flask_cors import CORS
import os
import secrets
import requests
from db import get_db_connection, init_db
from functools import wraps
import sqlite3

clientSecret = os.getenv("OIDC_CLIENT_SECRET")
clientID = os.getenv("OIDC_CLIENT_ID")
reDirect = 'http://localhost:8000/auth/callback'
frontend_url = os.getenv("FRONTEND_URL")
cal_api_key = os.getenv("CAL_NJ_API_KEY")
spoonacular_API_KEY = os.getenv("SPOONACULAR_API_KEY")
usda_api_key = os.getenv("USDA_API_KEY")

DEX_TOKEN_URL = 'http://dex:5556/token'
DEX_USERINFO_URL = 'http://dex:5556/userinfo'


app = Flask(__name__, static_folder='dist', static_url_path='')
CORS(app, supports_credentials=True, resources={r"/*": {"origins": frontend_url}})
app.secret_key = secrets.token_hex(16)
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
        email = userinfo.get('email', '')
        if email == 'moderator@FoodTracker.com':
            userinfo['role'] = 'moderator'
        elif email == 'admin@FoodTracker.com':
            userinfo['role'] = 'admin'
        else:
            userinfo['role'] = 'user'
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
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    cnx.close()
    return jsonify({
        "email": email,
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
@app.route('/api/quary_food', methods=['POST'])
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


@app.route('/report', methods=['GET'])
def get_report():
    user = session.get('user')
    if not user:
        return jsonify({"error": "not auth"}), 401

    email = user['email']
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT cal_budget, cal_eaten, cal_left, protein, carbs, fats
        FROM report_info
        WHERE email = ? AND report_date = DATE('now')
    """, (email,))
    row = cursor.fetchone()
    cursor.execute("""
        SELECT meal_type, food_name, grams
        FROM meal_entries
        WHERE email = ? AND report_date = DATE('now')
    """, (email,))
    meals_raw = cursor.fetchall()

    meal_list = {
        'breakfast': [],
        'lunch': [],
        'dinner': [],
        'snacks': []
    }

    for meal_type, food_name, grams in meals_raw:
        meal_list[meal_type].append({
            'name': food_name,
            'grams': grams
        })

    cursor.close()
    cnx.close()

    if row:
        report = {
            "calorieBudget": row[0],
            "calsAte": row[1],
            "calsLeft": row[2],
            "totalProtein": row[3],
            "totalCarbs": row[4],
            "totalFats": row[5],
            "mealList": meal_list  
        }
        return jsonify(report)
    else:
        return jsonify({"message": "No report found"}), 404

#database for report page
@app.route('/report', methods=['POST'])
def set_report():
    user = session.get('user')
    if not user:
        return jsonify({"error": "not auth"}), 401
    
    data = request.get_json()
    email = user['email']

    cal_budget = data.get('calorieBudget')
    cal_eaten = data.get('calsAte')
    cal_left = data.get('calsLeft')
    protein = data.get('totalProtein')
    carbs = data.get('totalCarbs')
    fats = data.get('totalFats')
    meal_list = data.get('mealList', {})  

    cnx = get_db_connection()
    cursor = cnx.cursor()

    cursor.execute("""
        INSERT INTO report_info (email, cal_budget, cal_eaten, cal_left, protein, carbs, fats, report_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, DATE('now'))
        ON CONFLICT(email, report_date) DO UPDATE SET
            cal_budget = excluded.cal_budget,
            cal_eaten = excluded.cal_eaten,
            cal_left = excluded.cal_left,
            protein = excluded.protein,
            carbs = excluded.carbs,
            fats = excluded.fats
    """, (email, cal_budget, cal_eaten, cal_left, protein, carbs, fats))
    cursor.execute("""
        DELETE FROM meal_entries WHERE email = ? AND report_date = DATE('now')
    """, (email,))


    for meal_type, items in meal_list.items():
        for item in items:
            food_name = item.get('name')
            grams = item.get('grams')
            if food_name and grams is not None:
                cursor.execute("""
                    INSERT INTO meal_entries (email, meal_type, food_name, grams, report_date)
                    VALUES (?, ?, ?, ?, DATE('now'))
                """, (email, meal_type, food_name, grams))

    cnx.commit()
    cursor.close()
    cnx.close()

    return jsonify({"message": "Report Saved with Meals"})




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
    query = request.args.get('query')
    limit = request.args.get('limit')
    min_calories = request.args.get('minCalories')
    max_calories = request.args.get('maxCalories')
    diets = request.args.getlist('diet')
    meal_types = request.args.getlist('mealType')

    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Missing food query"}), 400

    api_url = 'https://api.spoonacular.com/recipes/complexSearch'

    params = {
        'apiKey': spoonacular_API_KEY,
        'number': limit,
        'addRecipeInformation': True,
        'fillIngredients': True,
        'addRecipeInstructions': True,
    }

    if query:
        params['query'] = query
    if min_calories:
        params['minCalories'] = min_calories
    if max_calories:
        params['maxCalories'] = max_calories
    if diets:
        params['diet'] = ','.join(diets)
    if meal_types:
        params['type'] = ','.join(meal_types)


    def estimate_calories(ingredient_names):
        try:
            joined_query = ', '.join(ingredient_names)
            response = requests.post(
                'http://localhost:8000/report',
                headers={'Content-Type': 'application/json'},
                json={'query': joined_query}
            )
            if response.status_code == 200:
                data = response.json()
                return round(sum(item.get('calories', 0) for item in data.get('items', [])), 2)
            else:
                return None
        except Exception as e:
            print(f"[Calorie Estimation Error] {e}")
            return None

    try:
        res = requests.get(api_url, params=params)


        if res.status_code == 200:
            data = res.json()
            recipes = data.get('results', [])


            items = []
            for recipe in recipes:
                # Extract ingredients
                ingredients = []
                ingredient_names = []
                for ing in recipe.get('extendedIngredients', []):
                    amount = ing.get('amount', '')
                    unit = ing.get('unit', '')
                    name = ing.get('name', '')
                    ingredients.append(f"{amount} {unit} {name}".strip())
                    ingredient_names.append(name)

                # Extract instructions
                instructions = []
                for instruction_group in recipe.get('analyzedInstructions', []):
                    for step in instruction_group.get('steps', []):
                        instructions.append(step.get('step', ''))

                # Estimate calories from ingredient names
                calories = estimate_calories(ingredient_names)

                ingredients = [
                    f"{ing.get('amount', '')} {ing.get('unit', '')} {ing.get('name', '')}".strip()
                    for ing in recipe.get('extendedIngredients', [])
                ]

                instructions = [
                    step.get('step', '')
                    for instruction_group in recipe.get('analyzedInstructions', [])
                    for step in instruction_group.get('steps', [])
                ]

                item = {
                    'title': recipe.get('title', ''),
                    'ingredients': '|'.join(ingredients),
                    'instructions': '. '.join(instructions),
                    'servings': str(recipe.get('servings', '')),
                    'image': recipe.get('image', ''),
                    'calories': calories  #add Kcal
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

# search for food in USDA database
@app.route('/api/food/search', methods=['GET'])
def search_food():
    query = request.args.get('query', '')
    page_size = request.args.get('pageSize', 5)

    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    try:
        response = requests.get(
            'https://api.nal.usda.gov/fdc/v1/foods/search',
            params={
                'api_key': usda_api_key,
                'query': query,
                'dataType': ['Foundation', 'SR Legacy'],
                'pageSize': page_size
            }
        )
        response.raise_for_status()
        data = response.json()

        transformed_foods = [{
            'name': food.get('description', ''),
            'id': food.get('fdcId'),
            'brandOwner': food.get('brandOwner'),
            'category': (
                food.get('foodCategory', {}).get('description')
                if isinstance(food.get('foodCategory'), dict)
                else None
            )
        } for food in data.get('foods', [])]

        return jsonify({
            'foods': transformed_foods,
            'totalHits': data.get('totalHits', 0)
        })

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

# Announcement Role Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Announcements API
@app.route('/announcements', methods=['GET'])
def get_announcements():
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT id, content, created_by, created_at FROM announcements ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cnx.close()
    announcements = [
        {
            'id': row['id'],
            'content': row['content'],
            'created_by': row['created_by'],
            'created_at': row['created_at']
        }
        for row in rows
    ]
    return jsonify(announcements)

@app.route('/announcements', methods=['POST'])
@admin_required
def post_announcement():
    user = session.get('user')
    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Content required'}), 400
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute(
        "INSERT INTO announcements (content, created_by) VALUES (?, ?)",
        (content, user.get('email', 'admin'))
    )
    cnx.commit()
    ann_id = cursor.lastrowid
    cursor.execute("SELECT id, content, created_by, created_at FROM announcements WHERE id = ?", (ann_id,))
    row = cursor.fetchone()
    cnx.close()
    return jsonify({
        'id': row['id'],
        'content': row['content'],
        'created_by': row['created_by'],
        'created_at': row['created_at']
    })

@app.route('/announcements/<int:ann_id>', methods=['DELETE'])
@admin_required
def delete_announcement(ann_id):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("DELETE FROM announcements WHERE id = ?", (ann_id,))
    cnx.commit()
    cnx.close()
    return jsonify({'success': True})

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

# --- Goal Comments API ---
@app.route('/goal-comments', methods=['GET'])
def get_goal_comments():
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    user_email = request.args.get('user_email')
    # Allow admins to fetch comments for any user_email, or users to fetch their own comments
    if user.get('role') != 'admin' and user_email != user.get('email'):
        return jsonify({'error': 'Forbidden'}), 403
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT id, user_email, content, created_by, created_at, type, milestone FROM goal_comments WHERE user_email = ? ORDER BY created_at DESC", (user_email,))
    rows = cursor.fetchall()
    cnx.close()
    comments = [
        {
            'id': row['id'],
            'user_email': row['user_email'],
            'content': row['content'],
            'created_by': row['created_by'],
            'created_at': row['created_at'],
            'type': row['type'],
            'milestone': row['milestone']
        }
        for row in rows
    ]
    return jsonify(comments)

@app.route('/goal-comments', methods=['POST'])
@admin_required
def post_goal_comment():
    data = request.get_json()
    user_email = data.get('user_email')
    content = data.get('content')
    comment_type = data.get('type', 'manual')
    milestone = data.get('milestone')
    if not user_email or not content:
        return jsonify({'error': 'user_email and content required'}), 400
    user = session.get('user')
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute(
        "INSERT INTO goal_comments (user_email, content, created_by, type, milestone) VALUES (?, ?, ?, ?, ?)",
        (user_email, content, user.get('email', 'admin'), comment_type, milestone)
    )
    cnx.commit()
    comment_id = cursor.lastrowid
    cursor.execute("SELECT id, user_email, content, created_by, created_at, type, milestone FROM goal_comments WHERE id = ?", (comment_id,))
    row = cursor.fetchone()
    cnx.close()
    return jsonify({
        'id': row['id'],
        'user_email': row['user_email'],
        'content': row['content'],
        'created_by': row['created_by'],
        'created_at': row['created_at'],
        'type': row['type'],
        'milestone': row['milestone']
    })

@app.route('/goal-comments/<int:comment_id>', methods=['DELETE'])
@admin_required
def delete_goal_comment(comment_id):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("DELETE FROM goal_comments WHERE id = ?", (comment_id,))
    cnx.commit()
    cnx.close()
    return jsonify({'success': True})

@app.route('/users/list', methods=['GET'])
def list_users():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT email, name FROM users")
    users = [{'email': row['email'], 'name': row['name']} for row in cursor.fetchall()]
    cnx.close()
    return jsonify(users)

# post a meal
@app.route('/api/meal', methods=['POST'])
def add_meal():
    user = session.get('user')
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
        
    email = user['email']
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    cnx = get_db_connection()
    cursor = cnx.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO meals (
                name, date_created, ingredients, user_email
            ) VALUES (?, datetime('now'), ?, ?)
        """, (
            data['name'],
            '',  # Empty string for initial ingredients
            email
        ))
        
        # Get the ID of the newly inserted meal
        meal_id = cursor.lastrowid
        
        cnx.commit()
        return jsonify({
            'message': 'Meal added successfully!',
            'meal_name': data['name'],
            'meal_id': meal_id
        })
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cnx.close()

# get user's meals
@app.route('/api/meal', methods=['GET'])
def get_meals():
    user = session.get('user')
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
        
    email = user['email']
    cnx = get_db_connection()
    cursor = cnx.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, date_created, ingredients
            FROM meals 
            WHERE user_email = ?
            ORDER BY date_created DESC
        """, (email,))
        
        meals = []
        for row in cursor.fetchall():
            meals.append({
                'id': row['id'],
                'name': row['name'],
                'date_created': row['date_created'],
                'ingredients': row['ingredients'].split('|') if row['ingredients'] else []
            })
            
        return jsonify({'meals': meals})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cnx.close()

# delete a meal
@app.route('/api/meal/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    user = session.get('user')
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
        
    email = user['email']
    cnx = get_db_connection()
    cursor = cnx.cursor()
    
    try:
        # First verify the meal belongs to the user
        cursor.execute("""
            SELECT 1 FROM meals 
            WHERE id = ? AND user_email = ?
        """, (meal_id, email))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Meal not found or unauthorized'}), 404
            
        # Delete the meal
        cursor.execute("""
            DELETE FROM meals 
            WHERE id = ? AND user_email = ?
        """, (meal_id, email))
        
        cnx.commit()
        return jsonify({'message': 'Meal deleted successfully'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cnx.close()

# update a meal
@app.route('/api/meal/<int:meal_id>', methods=['PUT'])
def update_meal(meal_id):
    user = session.get('user')
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
        
    email = user['email']
    data = request.get_json()
    
    cnx = get_db_connection()
    cursor = cnx.cursor()
    
    try:
        # First verify the meal belongs to the user
        cursor.execute("""
            SELECT 1 FROM meals 
            WHERE id = ? AND user_email = ?
        """, (meal_id, email))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Meal not found or unauthorized'}), 404
        
        # Build update query based on provided fields
        update_fields = []
        params = []
        if 'name' in data:
            update_fields.append('name = ?')
            params.append(data['name'])
        if 'ingredients' in data:
            update_fields.append('ingredients = ?')
            params.append('|'.join(data['ingredients']) if isinstance(data['ingredients'], list) else data['ingredients'])
            
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
            
        # Add meal_id and email to params
        params.extend([meal_id, email])
        
        # Update the meal
        cursor.execute(f"""
            UPDATE meals 
            SET {', '.join(update_fields)}
            WHERE id = ? AND user_email = ?
        """, params)
        
        cnx.commit()
        return jsonify({'message': 'Meal updated successfully'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cnx.close()

# get a specific meal
@app.route('/api/meal/<int:meal_id>', methods=['GET'])
def get_meal(meal_id):
    user = session.get('user')
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
        
    email = user['email']
    
    cnx = get_db_connection()
    cursor = cnx.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, ingredients 
            FROM meals 
            WHERE id = ? AND user_email = ?
        """, (meal_id, email))
        
        meal = cursor.fetchone()
        
        if not meal:
            return jsonify({'error': 'Meal not found or unauthorized'}), 404
            
        meal_data = {
            'id': meal[0],
            'name': meal[1],
            'ingredients': meal[2].split('|') if meal[2] else []
        }
        
        return jsonify(meal_data)
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cnx.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8000)
