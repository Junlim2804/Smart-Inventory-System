from flask import Flask,current_app,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,current_user
import urllib
from functools import wraps
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
    app.register_error_handler(404, page_not_found)
    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .vendor import vendor as vendor_blueprint
    app.register_blueprint(vendor_blueprint)

    return app

def page_not_found(e):
  return render_template('404.html'), 404
  
def role(role="ANY"):
   def wrapper(fn):
      @wraps(fn)
      def decorated_view(*args, **kwargs):

         if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
         urole = current_user.get_urole()
         if ( (urole != role) and (role != "ANY")):
            return current_app.login_manager.unauthorized()      
         return fn(*args, **kwargs)
      return decorated_view
   return wrapper
app=create_app()