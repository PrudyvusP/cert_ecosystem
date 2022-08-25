from flask import Blueprint
from flask_restful import Api, Resource
from flask_pydantic import validate
from organizations.models import Region
from .serializers import RegionPostModel
from flask_restful import reqparse
api_bp = Blueprint('api', __name__)
api = Api(api_bp)
post_parser = reqparse.RequestParser()

class TodoItem(Resource):

    def get(self, region_id):
        print(self.methods)
        try:
            region = Region.query.get(region_id)
            return {"region": region.name}
        except Exception as e:
            print(e.message)


class TodoPost(Resource):
    @validate(body=RegionPostModel)
    def post(self):
        args = post_parser.parse_args()
        print(args)

api.add_resource(TodoItem, '/regions/<int:region_id>')
api.add_resource(TodoPost, '/regions/')
