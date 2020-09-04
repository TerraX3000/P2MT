from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, MetaData
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# Third-party libraries for login authorization and management
from authlib.integrations.flask_client import OAuth
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)


# This function is necessary to perform cacade deletes in SQLite
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Instantiate the database
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
# Instantiate up the login_manager
login_manager = LoginManager()
# Instantiate oauth for managing authentication
oauth = OAuth()


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.jinja_env.globals.update(zip=zip)
    # Initialize the database with the app
    db.init_app(app)
    # Initialize Migrate with the app and the database
    migrate.init_app(app, db)

    # Set up for using Google Login and API (if running on Google Cloud)
    useGoogleLoginAndAPI = app.config.get("USE_GOOGLE_LOGIN_AND_API")
    print("useGoogleLoginAndAPI =", useGoogleLoginAndAPI)
    if useGoogleLoginAndAPI:
        # User session management setup
        # https://flask-login.readthedocs.io/en/latest
        login_manager.init_app(app)

        # OAuth 2 client setup
        GOOGLE_DISCOVERY_URL = (
            "https://accounts.google.com/.well-known/openid-configuration"
        )
        oauth.init_app(app)
        oauth.register(
            name="google",
            server_metadata_url=GOOGLE_DISCOVERY_URL,
            client_kwargs={"scope": "openid email profile"},
        )

    from P2MT_App.main.routes import main_bp
    from P2MT_App.classAttendance.routes import classAttendance_bp
    from P2MT_App.dailyAttendance.routes import dailyAttendance_bp
    from P2MT_App.fetTools.routes import fetTools_bp
    from P2MT_App.interventionInfo.routes import interventionInfo_bp
    from P2MT_App.masterSchedule.routes import masterSchedule_bp
    from P2MT_App.scheduleAdmin.routes import scheduleAdmin_bp
    from P2MT_App.schoolCalendar.routes import schoolCalendar_bp
    from P2MT_App.studentInfo.routes import studentInfo_bp
    from P2MT_App.p2mtAdmin.routes import p2mtAdmin_bp
    from P2MT_App.parentInfo.routes import parentsInfo_bp
    from P2MT_App.tmiTeacherReview.routes import tmiTeacherReview_bp
    from P2MT_App.tmiFinalApproval.routes import tmiFinalApproval_bp
    from P2MT_App.googleAPI.routes import googleAPI_bp
    from P2MT_App.errors.handlers import errors_bp
    from P2MT_App.learningLab.routes import learningLab_bp
    from P2MT_App.p2mtTemplates.routes import p2mtTemplates_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(classAttendance_bp)
    app.register_blueprint(dailyAttendance_bp)
    app.register_blueprint(fetTools_bp)
    app.register_blueprint(interventionInfo_bp)
    app.register_blueprint(masterSchedule_bp)
    app.register_blueprint(scheduleAdmin_bp)
    app.register_blueprint(schoolCalendar_bp)
    app.register_blueprint(studentInfo_bp)
    app.register_blueprint(p2mtAdmin_bp)
    app.register_blueprint(parentsInfo_bp)
    app.register_blueprint(tmiTeacherReview_bp)
    app.register_blueprint(tmiFinalApproval_bp)
    app.register_blueprint(googleAPI_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(learningLab_bp)
    app.register_blueprint(p2mtTemplates_bp)

    return app
