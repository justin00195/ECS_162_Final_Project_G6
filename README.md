# ECS_162_Final_Project_G6


## install package in backend
```
cd backend
pip install -r requirements.txt
```

## run backend server:
```
export FLASK_APP=app.py
flask run
```

## install package in frontend
```
cd frontend
npm install
npm run dev
npm install -D @tsconfig/svelte
npm install -D typescript svelte-check svelte-preprocess @sveltejs/vite-plugin-svelte vite svelte-spa-router

```
## run frontend 

```
npm run dev
```

## run full stack 
docker compose -f docker-compose.dev.yml up --build



### Backend Test: (Folder: backend)
```
pip install pytest
cd backend
pip install -r requirements.txt
pytest

```
The beginning tests are for API mock test.

The last two tests are to check third-party API tests

Citation: 
[pytest](https://docs.pytest.org/en/6.2.x/reference.html#pytest-fixture)