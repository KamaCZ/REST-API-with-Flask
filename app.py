import flask
from flask import Flask, jsonify
import os
from flask_smorest import Api
from flask_jwt_extended import JWTManager
import secrets
from flask_migrate import Migrate

from db import db
from blocklist import BLOCKLIST
import models


from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint


def create_app(db_url=None):
    app = Flask(__name__)

    # Flask Config
    # so that we can see exceptions from flask and propagate it here
    app.config["PROPAGATE_EXCEPTIONS"] = True
    # flask-smorest Config
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    # documentation connection
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)

    # connecting flask-smorest to the flask app
    api = Api(app)

    # app.config["JWT_SECRET_KEY"] = secrets.SystemRandom().getrandbits(128)
    app.config["JWT_SECRET_KEY"] = "147709512869931887548979268486789062085"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def rewoked_token_callback(jwt_header, jwt_payload):
        # should be more like look in the database and see whether the user is ad admin
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_rewoked"}
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fesh_callback(jwt_header, jwt_payload):
        return jsonify(
            {"description": "The token is not fresh", "error": "fresh_token_required"}
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # should be more like look in the database and see whether the user is ad admin
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.invalid_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_required"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    # @app.before_first_request
    # def create_tables():
    #     db.create_all()

    with app.app_context():
        db.create_all()

    # registering blueprints
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
