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