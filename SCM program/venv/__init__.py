from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
import urllib
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
server = '(localdb)\MSSQLLocalDB'
database = 'SCMdb'
username = 'Guest'
password = 'Guest'
driver= '{ODBC Driver 17 for SQL Server}'

def create_app():
    app = Flask(__name__)
    app.config['TESTING'] = True

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    
    params = urllib.parse.quote_plus("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")
    app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .vendor import vendor as vendor_blueprint
    app.register_blueprint(vendor_blueprint)

    return app