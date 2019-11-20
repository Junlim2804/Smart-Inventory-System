@echo off
CALL C:\Users\magic\Anaconda3\Scripts\activate.bat C:\Users\magic\Anaconda3\envs\pmdarima

set flask_app=venv
set flask_env=development
set flask_debug=1

python -m flask run --host=0.0.0.0
