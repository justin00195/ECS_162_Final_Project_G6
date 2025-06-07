DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS goals;

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