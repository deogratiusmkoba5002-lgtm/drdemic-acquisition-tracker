import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from sqlalchemy import text
from flask_migrate import Migrate

from models.db import db

load_dotenv()

migrate = Migrate()

def create_app():
  app = Flask(__name__)

  app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
  app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

  db.init_app(app)
  migrate.init_app(app, db)

  @app.route("/health", methods=["GET"])
  def health_check():
    try:
      db.session.execute(text("SELECT 1"))
      return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception:
      return jsonify({"status": "unhealthy", "database": "unreachable"}), 503

  from routes.schools import bp as schools_bp
  from routes.pages import bp as pages_bp

  app.register_blueprint(schools_bp)
  app.register_blueprint(pages_bp)

  return app

app = create_app()

if __name__ == "__main__":
  app.run(debug=True)