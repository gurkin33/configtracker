from datetime import datetime, timedelta
from ua_parser import user_agent_parser
from werkzeug.user_agent import UserAgent
from werkzeug.utils import cached_property
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jti
from respect_validation import Validator as v, FormValidator as fv
from sqlalchemy import and_

from api.config import GlobalConfig
from api.db import db
from api.src.models import UserModel, SessionModel


class AuthLogin(Resource):

    @classmethod
    def post(cls):
        data = request.get_json()
        client_info = ''
        user_agent = ParsedUserAgent(request.headers.get('User-Agent'))
        if user_agent.platform:
            client_info += user_agent.platform
        if user_agent.browser and user_agent.version:
            client_info += f"({user_agent.browser} {user_agent.version})"
        if user_agent.browser and not user_agent.version:
            client_info += f"({user_agent.browser})"
        if cls._brut_force_detect(request.remote_addr):
            return {"error": [f"You blocked for {GlobalConfig.BRUT_FORCE_TIMEOUT} minutes"]}, 403
        session = SessionModel(ip_address=request.remote_addr, client=client_info)
        session.save()
        validation = fv()
        validation.validate(data, {
            "username": v.string_type().not_empty(),
            "password": v.string_type().not_empty()
        })
        if validation.failed():
            return {"validation": validation.get_messages()}, 400

        user = UserModel.find_by_username(data['username'])

        if user and user.check_password(data['password']):
            if user.change_password:
                return {"errors": ["Authentication failed", "Change password required"], "change_password": True}, 401
            token_created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            token_expired_at = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            additional_claims = {
                'user': user.get(permissions=True),
                'token_created_at': token_created_at,
                'token_expired_at': token_expired_at,
            }
            access_token = create_access_token(
                identity={
                    'username': additional_claims['user']['username'],
                    'id': additional_claims['user']['id'],
                },
                fresh=True,
                additional_claims=additional_claims
            )
            refresh_token = create_refresh_token(identity={
                    'username': additional_claims['user']['username'],
                    'id': additional_claims['user']['id'],
                })
            resp = jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_create_at': token_created_at,
                'token_expired_at': token_expired_at,
                # 'user': user.get()
            })
            # set_access_cookies(resp, access_token)
            # print(get_jti(access_token))
            session.user_id = user.id
            session.access_jti = get_jti(access_token)
            session.refresh_jti = get_jti(refresh_token)
            session.save()
            return resp

        return {"errors": ["Authentication failed"]}, 401

    @classmethod
    def _brut_force_detect(cls, ipaddr: str):
        brut_force_timeout = datetime.utcnow() - timedelta(minutes=GlobalConfig.BRUT_FORCE_TIMEOUT)
        too_old_timeout = datetime.utcnow() - timedelta(days=1)
        #  delete rows by brut force timeout
        SessionModel.query.filter(and_(
            SessionModel.created_at < brut_force_timeout, SessionModel.user_id.is_(None))).delete()
        #  delete too old rows
        SessionModel.query.filter(SessionModel.created_at < too_old_timeout).delete()
        db.session.commit()
        return SessionModel.query.filter(
            and_(SessionModel.ip_address == ipaddr,
                 SessionModel.user_id.is_(None))).count() >= GlobalConfig.BRUT_FORCE_ATTEMPTS


class AuthLogout(Resource):

    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()["jti"]
        SessionModel.delete_by_jti(access_jti=jti)
        return True


class AuthChangePassword(AuthLogin):

    @classmethod
    def post(cls):
        data = request.get_json()
        client_info = ''
        user_agent = ParsedUserAgent(request.headers.get('User-Agent'))
        if user_agent.platform:
            client_info += user_agent.platform
        if user_agent.browser and user_agent.version:
            client_info += f"({user_agent.browser} {user_agent.version})"
        if user_agent.browser and not user_agent.version:
            client_info += f"({user_agent.browser})"
        if cls._brut_force_detect(request.remote_addr):
            return {"error": [f"You blocked for {GlobalConfig.BRUT_FORCE_TIMEOUT} minutes"]}, 403
        session = SessionModel(ip_address=request.remote_addr, client=client_info)
        session.save()
        validation = fv()
        validation.validate(data, {
            "username": v.string_type().not_empty(),
            "password": v.string_type().not_empty(),
            "new_password": v.string_type().not_empty().length(min_value=8, max_value=64)
        })
        if validation.failed():
            return {"validation": validation.get_messages()}, 400

        user = UserModel.find_by_username(data['username'])

        if user and user.check_password(data['password']):
            user.password = UserModel.hash_password(data['new_password'])
            user.change_password = False
            user.save()
            return True

        return {"errors": ["Authentication failed"]}, 401


class AuthRefreshToken(Resource):

    @classmethod
    @jwt_required(refresh=True)
    def get(cls):
        try:
            claims = get_jwt()
        except:
            return {"error": ['Access Restricted!']}, 401
        _user = claims.get('sub')
        # print(claims)
        # print(request.headers.get('Authorization'))
        if not _user:
            return {"error": ['Access Restricted!']}, 401

        if not _user.get('id'):
            return {"error": ['Access Restricted!']}, 401

        user = UserModel.find_by_id(_user.get('id'))

        if not user:
            return {"error": ['Access Restricted!']}, 401

        token_created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        token_expired_at = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        additional_claims = {
            'user': user.get(permissions=True),
            'token_created_at': token_created_at,
            'token_expired_at': token_expired_at,
        }
        access_token = create_access_token(
            identity={
                'username': additional_claims['user']['username'],
                'user_id': additional_claims['user']['id'],
            },
            fresh=True,
            additional_claims=additional_claims
        )
        refresh_token = request.headers.get('Authorization').replace('Bearer ', '')
        session = SessionModel.find_by_refresh_jti(get_jti(refresh_token))
        if not session:
            return {"error": ['Access Restricted!']}, 401
        session.delete_child_jti()
        session.delete_by_refresh_jti()
        session.new_jti = get_jti(access_token)
        session.save()
        new_session = SessionModel(
            ip_address=session.ip_address,
            access_jti=get_jti(access_token),
            refresh_jti=session.refresh_jti,
            user_id=session.user_id,
        )
        new_session.save()
        return {
                   'access_token': access_token,
                   'refresh_token': refresh_token,
                   'token_create_at': token_created_at,
                   'token_expired_at': token_expired_at,
               }, 200


class ParsedUserAgent(UserAgent):
    @cached_property
    def _details(self):
        return user_agent_parser.Parse(self.string)

    @property
    def platform(self):
        return self._details['os']['family']

    @property
    def browser(self):
        return self._details['user_agent']['family']

    @property
    def version(self):
        return '.'.join(
            part
            for key in ('major', 'minor', 'patch')
            if (part := self._details['user_agent'][key]) is not None
        )