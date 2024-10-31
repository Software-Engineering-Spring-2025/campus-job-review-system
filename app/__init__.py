from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.job_fetcher import fetch_job_listings
import pytz

cached_jobs = []


def refresh_job_data():
    global cached_jobs
    cached_jobs = fetch_job_listings()
    print(cached_jobs)
    socketio.emit("update_jobs", cached_jobs)


scheduler = BackgroundScheduler()

scheduler.add_job(
    refresh_job_data, "interval", seconds=5, timezone=pytz.timezone("America/New_York")
)

print(scheduler)
scheduler.start()


app = Flask(__name__)
socketio = SocketIO(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
migrate = Migrate(app, db, render_as_batch=True)


@app.before_first_request
def create_table():
    db.create_all()


from app import routes, models
