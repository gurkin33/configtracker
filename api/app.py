from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_migrate import Migrate

from api.db import db
from api.routes import RouteMaker

from api.src.models.session import SessionModel

from respect_validation import Factory
Factory.add_rules_packages('api.src.validation.rules')
Factory.add_exceptions_packages('api.src.validation.exceptions')

app = Flask(__name__)
app.config.from_object("api.config.GlobalConfig")
CORS(app, supports_credentials=True, allow_headers='*')

# flask_restful
api = Api(app, prefix='/api')
# flask_jwt_extended
jwt = JWTManager(app)
# flask_sqlalchemy
db.init_app(app)
# flask_migrate
migrate = Migrate(app, db)
migrate.init_app(app)


@app.errorhandler(404)
def page_not_found(e):
    return request.url, 404


# NoAuthorizationError
@jwt.expired_token_loader
def expired_token_callback(callback, arg):
    return jsonify({
        'errors': ['Token has expired']
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'errors': ['Wrong token']
    }), 401


@jwt.unauthorized_loader
def unauthorised_callback(error):
    return jsonify({
        'errors': ['Authorization header required']
    }), 401


@jwt.needs_fresh_token_loader
def needs_fresh_token_callback(error):
    return jsonify({
        'errors': ['Token is not fresh']
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload: dict):
    return jsonify({
        'errors': ['Token has been revoked']
    }), 401


@jwt.token_verification_failed_loader
def token_verification_failed_loader(jwt_header, jwt_payload: dict):
    return jsonify({
        'errors': ['Token verification failed']
    }), 401


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    if jwt_payload.get('type', None) and jwt_payload.get('type') == 'refresh':
        return not bool(SessionModel.query.filter(SessionModel.refresh_jti == jti).count())
    else:
        return not bool(SessionModel.query.filter(SessionModel.access_jti == jti).count())


RouteMaker.run(api=api)
