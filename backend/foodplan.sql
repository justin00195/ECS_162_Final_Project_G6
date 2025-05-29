DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS goals;

CREATE TABLE users (
  email TEXT PRIMARY KEY,
  name TEXT,
  gender TEXT,
  age INTEGER,
  height REAL,
  weight REAL,
  activity_level REAL
);

CREATE TABLE goals (
    email TEXT PRIMARY KEY,
    target_weight REAL,
    duration_days INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email) REFERENCES users(email)
);