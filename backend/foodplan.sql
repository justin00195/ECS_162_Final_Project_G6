DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS goal_comments;
DROP TABLE IF EXISTS report_info;
DROP TABLE IF EXISTS meal_entries;

CREATE TABLE IF NOT EXISTS users (
  email TEXT PRIMARY KEY,
  name TEXT,
  gender TEXT,
  age INTEGER,
  height REAL,
  weight REAL,
  activity_level REAL
);

CREATE TABLE IF NOT EXISTS goals (
    email TEXT PRIMARY KEY,
    goal_type TEXT NOT NULL CHECK(goal_type IN ('lose','maintain','gain')),
    starting_weight REAL NOT NULL,
    latest_weight REAL NOT NULL,
    target_weight REAL NOT NULL,
    duration_days INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    FOREIGN KEY (email) REFERENCES users(email)
);

CREATE TABLE IF NOT EXISTS favorite_recipes (
  email TEXT,
  recipe_title TEXT,
  PRIMARY KEY (email, recipe_title),
  FOREIGN KEY (email) REFERENCES users(email)
);

DROP TABLE IF EXISTS announcements;

CREATE TABLE IF NOT EXISTS announcements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content TEXT NOT NULL,
  created_by TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS goal_comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_email TEXT NOT NULL,
  content TEXT NOT NULL,
  created_by TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  type TEXT NOT NULL CHECK(type IN ('manual','template','auto')),
  milestone INTEGER,
  FOREIGN KEY (user_email) REFERENCES users(email)
);


CREATE TABLE IF NOT EXISTS report_info (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email VARCHAR(255), 
  cal_budget INT,
  cal_eaten INT,
  cal_left INT,
  protein FLOAT,
  carbs FLOAT,
  fats FLOAT,
  report_date DATE NOT NULL,
 UNIQUE(email,report_date)
);

CREATE TABLE IF NOT EXISTS meal_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  meal_type TEXT NOT NULL CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snacks')),
  food_name TEXT NOT NULL,
  grams REAL NOT NULL,
  report_date DATE NOT NULL,
  FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS meals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  date_created TIMESTAMP,
  ingredients TEXT,
  user_email TEXT NOT NULL,
  FOREIGN KEY (user_email) REFERENCES users(email)
);