import pytest
from app import app as flask_app
from app import get_db_connection


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test_secret'
    with flask_app.test_client() as client:
        yield client

def test_usernologin(client):
    res = client.get('/auth/user')
    assert res.status_code in [401, 403, 500]  

def test_withoutlogin(client):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("DELETE FROM users WHERE email = ?", ('unittest@FoodTracker.com',))
    cursor.execute("""
        INSERT INTO users (email, name, gender, age, height, weight, activity_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('unittest@FoodTracker.com', 'Test User', 'male', 25, 175, 70, 1.5))

    cnx.commit()
    cnx.close()
    with client.session_transaction() as sess:
        sess['user'] = {'email': 'unittest@FoodTracker.com'}
    res = client.get('/calculate')
    assert res.status_code == 200

def test_report(client):
    with client.session_transaction() as sess:
        sess['user'] = {'email': 'unittest@FoodTracker.com'}
    res = client.get('/report')
    assert res.status_code in [200, 404]

def test_goal(client):
    with client.session_transaction() as sess:
        sess['user'] = {'email': 'unittest@FoodTracker.com'}
    res = client.get('/goal')
    assert res.status_code in [200, 404]

def test_fallback(client):
    res = client.get('/nonexistent')
    assert res.status_code in [404, 200]  


def test_savegoal(client):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (email, name, gender, age, height, weight, activity_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('unittest@FoodTracker.com', 'Test User', 'male', 25, 175, 70, 1.5))
    cnx.commit()
    cnx.close()

    with client.session_transaction() as sess:
        sess['user'] = {'email': 'unittest@FoodTracker.com'}

    res = client.post('/goal', json={
        'goal_type': 'lose',
        'starting_weight': 70,
        'latest_weight': 69,
        'target_weight': 65,
        'duration_days': 60,
        'start_date': '2025-06-01'
    })

    print("Response:", res.status_code, res.json)
    assert res.status_code == 200
    assert 'calories_sug' in res.json
    assert res.json['message'] == 'Goal saved successfully!'
