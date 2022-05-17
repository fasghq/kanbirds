from flask import request, json, Response, Blueprint
from ..models.BirdModel import BirdModel, BirdSchema
from ..shared.Authentication import Auth

bird_api = Blueprint('birds', __name__)
bird_schema = BirdSchema()


@bird_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
  birds = BirdModel.get_all_birds()
  ser_birds = bird_schema.dump(birds, many=True)
  return custom_response(ser_birds, 200)
  

@bird_api.route('/<int:bird_id>', methods=['GET'])
@Auth.auth_required
def get_a_bird(bird_id):
  bird = BirdModel.get_one_bird(bird_id)
  if not bird:
    return custom_response({'error': 'bird not found'}, 404)
  
  ser_bird = bird_schema.dump(bird)
  return custom_response(ser_bird, 200)


def custom_response(res, status_code):
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )

