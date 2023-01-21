from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.models import NodeModel


class Node(Resource):

    """"
    Node resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, node_id: str = ''):
        if not node_id:
            return {"error": ["Node ID must be present!"]}, 400
        node = NodeModel.find_by_id(_id=node_id)
        if not node:
            return {"error": ["Node not found"]}, 404
        return node.get(), 200

    @classmethod
    @access_checker(['manager'])
    def post(cls):
        node_json = request.get_json()
        v = NodeModel.validate(node=node_json)
        if v.failed():
            return {'validation': v.get_messages()}, 400

        new_node = NodeModel(**node_json)
        new_node.save()

        return new_node.get(), 200

    @classmethod
    @access_checker(['manager'])
    def put(cls, node_id: str = ''):
        if not node_id:
            return {"error": ["Node ID must be present!"]}, 400
        node = NodeModel.find_by_id(_id=node_id)
        if not node:
            return {"error": ["Node not found"]}, 404

        node_json = request.get_json()
        v = NodeModel.validate(node=node_json, _id=node_id)

        if v.failed():
            return {'validation': v.get_messages()}, 400

        node.update(data=node_json)
        node.save()

        return node.get(), 200

    @classmethod
    @access_checker(['manager'])
    def delete(cls, node_id: str = ''):
        if not node_id:
            return {"error": ["Node ID must be present!"]}, 400
        node = NodeModel.find_by_id(_id=node_id)
        if not node:
            return {"error": ["Node not found"]}, 404

        if NodeModel.get_ref_count(node_id):
            return {"error": ["Node has references!"]}, 400

        node.delete()

        return {"result": True}, 200
