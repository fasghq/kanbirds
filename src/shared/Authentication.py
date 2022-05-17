import jwt
import os
import datetime
from flask import json, Response, request, g
from functools import wraps
from ..models.BirdModel import BirdModel
from ..models.UserModel import UserModel


class Auth():
  @staticmethod
  def generate_token(user_id):
    try:
      payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
      }
      secret_key = 'kanaria22'
      return jwt.encode(
        payload,
        secret_key,
        'HS256'
      )
    except Exception as e:
      return Response(
        mimetype="application/json",
        response=json.dumps({'error': 'error in generating user token'}),
        status=400
      )

  @staticmethod
  def auth_required(func):
    @wraps(func)
    def decorated_auth(*args, **kwargs):
      if 'api-token' not in request.headers:
        return Response(
          mimetype="application/json",
          response=json.dumps({'error': 'Authentication token is not available, please login to get one'}),
          status=400
        )
      token = request.headers.get('api-token')
      data = Auth.decode_token(token)
      if data['error']:
        return Response(
          mimetype="application/json",
          response=json.dumps(data['error']),
          status=400
        )
        
      user_id = data['data']['user_id']
      check_user = UserModel.get_one_user(user_id)
      if not check_user:
        return Response(
          mimetype="application/json",
          response=json.dumps({'error': 'user does not exist, invalid token'}),
          status=400
        )
      g.user = {'id': user_id}
      return func(*args, **kwargs)
    return decorated_auth

  @staticmethod
  def decode_token(token):
    re = {'data': {}, 'error': {}}
    try:
      secret_key = 'kanaria22'
      payload = jwt.decode(token, secret_key, 'HS256')
      re['data'] = {'user_id': payload['sub']}
      return re
    except jwt.ExpiredSignatureError as e1:
      re['error'] = {'message': 'token expired, please login again'}
      return re
    except jwt.InvalidTokenError:
      re['error'] = {'message': 'Invalid token, please try again with a new token'}
      return re