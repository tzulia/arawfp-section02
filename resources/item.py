from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required

from models.item import ItemModel

from schemas.item import ItemSchema

# Message Strings Start #
PARSER_BLANK_ERROR = "'{}' cannot be blank."
ITEM_NOT_FOUND_ERROR = "Item not found"
ITEM_ALREADY_EXISTS_ERROR = "Item already exists!"
ITEM_STORE_NOT_FOUND_ERROR = "A Store with the name '{}' was not found."
ITEM_DB_ERROR = "The server did not answer in time, please try again later."
ITEM_DELETED_SUCCESSFULLY = "Item {} deleted!"
# Message String End #

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    @jwt_required
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)

        if item:
            return item_schema.dump(item)

        return {"error": ITEM_NOT_FOUND_ERROR}, 404

    @classmethod
    @jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"error": ITEM_ALREADY_EXISTS_ERROR}, 400

        new_item = item_schema.load(request.get_json())

        try:
            new_item.save_to_db()
        except Exception:
            return {"error": ITEM_DB_ERROR}, 500

        return item_schema.dump(new_item), 201

    @classmethod
    @jwt_required
    def put(cls, name: str):
        updated_item = item_schema.load(request.get_json())

        item = ItemModel.find_by_name(name)
        if item:
            # Update it
            item.price = updated_item.price

            item.store_id = updated_item.store_id

            try:
                item.save_to_db()
            except Exception:
                return {"error": ITEM_DB_ERROR}, 500

            return item_schema.dump(item)
        else:
            # Create it.
            try:
                updated_item.save_to_db()
            except Exception:
                return {"error": ITEM_DB_ERROR}, 500

            return item_schema.dump(updated_item), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if not item:
            return {"error": ITEM_NOT_FOUND_ERROR}, 400

        item.delete_from_db()

        return {"message": ITEM_DELETED_SUCCESSFULLY.format(name)}


class ItemList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        return {"items": item_list_schema.dump(ItemModel.find_all())}
