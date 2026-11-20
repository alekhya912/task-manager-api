from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text
import os,math
from flask import Flask, jsonify, request, abort, render_template
import logging
from extensions import db
from models import Task
from routes import tasks_bp

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)

app.register_blueprint(tasks_bp)

# Flask Migrate
migrate = Migrate(app, db)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/db-test")
def db_test():
    try:
        db.session.execute(text("SELECT 1"))
        return "Database connected successfully!"

    except Exception as e:
        return f"Database connection failed: {e}", 500

@app.errorhandler(500)
def internal_server_error(error):
    logger.error("Internal server error: %s", error)

    return jsonify({
        "message": "Internal server error"
    }), 500

@app.route("/test-error",methods=["GET"])
def test_error():
    abort(500)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "message": "Endpoint not found"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "message": "Method not allowed"
    }), 405

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "message": "Bad request"
    }), 400

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)