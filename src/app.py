from flask import Flask
from .config import app_config
from .models import db, bcrypt
from .view.BirdView import bird_api as bird_blueprint
from .view.UserView import user_api as user_blueprint

def create_app(env_name):
  app = Flask(__name__)

  app.config.from_object(app_config[env_name])

  bcrypt.init_app(app)

  db.init_app(app)

  app.register_blueprint(bird_blueprint, url_prefix='/api/v1/birds')

  app.register_blueprint(user_blueprint, url_prefix='/api/v1/users')

  @app.route('/', methods=['GET'])
  def index():
    return 'Congratulations! Kanbirds endpoint is working'

  return app