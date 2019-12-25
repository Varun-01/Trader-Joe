# Import Modules
from flask import Flask
from flask_login import LoginManager

# Import Python files from project
from .routing import appRoutes
from .models import db, User

# Code for app start up and back end functions
app = Flask(__name__)
appRoutes(app)

# Login set up
login = LoginManager(app)
# This is the default route that users get redirected to if they try to access a page
# that requires registration
login.login_view = "login"
app.secret_key = "test_secret"

# Database set-up
mysql_user = "root"
mysql_pass = "team13"
db_port = 3306
# This is the name of the database being used by the website
db_name = "appdb"

app.config['SQLALCHEMY_DATABASE_URI'] = r"mysql://%s:%s@127.0.0.1:%s/%s?charset=utf8mb4" % (mysql_user,
                                                                                            mysql_pass,
                                                                                            db_port,
                                                                                            db_name)
db.init_app(app)

# This code will reset and recreate all tables in the database.
# Only use this code when wiping the database
# with app.app_context():
#     db.drop_all()
#     db.create_all()
#     db.session.commit()


@login.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    app.run()
