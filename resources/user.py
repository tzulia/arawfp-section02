from flask_restful import Resource
from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)
from flask_jwt_extended import jwt_required
from werkzeug.security import safe_str_cmp
from marshmallow import EXCLUDE, ValidationError

from models.user import UserModel
from models.token_blacklist import BlacklistToken

from schemas.user import UserDataSchema

# Message Strings Start #
USER_NOT_FOUND_ERROR = "User not found"
PARSER_BLANK_ERROR = "'{}' cannot be blank."
USER_DELETED_SUCCESSFULLY = "User successfully deleted!"
USER_ALREADY_EXISTS_ERROR = "User {} already exists!"
USER_CREATED_SUCCESSFULLY = "User created successfully."
USER_LOGIN_SUCCESSFULLY = "User logged in successfully."
USER_LOGOUT_SUCCESSFULLY = "User logged out successfully."
TOKEN_AUTH_INVALID_CREDENTIALS = "Invalid credentials"
# Message Strings End #

user_schema = UserDataSchema(unknown=EXCLUDE)


class User(Resource):
    @classmethod
    @jwt_required
    @UserModel.require_admin
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"error": USER_NOT_FOUND_ERROR}, 404
        return user_schema.dump(user), 200

    @classmethod
    @jwt_required
    @UserModel.require_admin
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"error": USER_NOT_FOUND_ERROR}, 404

        user.delete_from_db()
        return {"message": USER_DELETED_SUCCESSFULLY}


class UserList(Resource):
    @classmethod
    @jwt_required
    @UserModel.require_admin
    def get(cls):
        return {"users": [user_schema.dump(user) for user in UserModel.get_all()]}


class UserRegister(Resource):
    @classmethod
    def post(cls):
        try:
            user_json = request.get_json()
            user_data = user_schema.load(user_json)
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(user_data["username"]):
            return (
                {"error": USER_ALREADY_EXISTS_ERROR.format(user_data["username"])},
                400,
            )

        if user_data["username"] == "tzulia":
            user_data["is_admin"] = True
        else:
            user_data["is_admin"] = False

        new_user = UserModel(**user_data)
        new_user.save_to_db()

        return {"message": USER_CREATED_SUCCESSFULLY}, 201


class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from parser
        try:
            user_json = request.get_json()
            user_data = user_schema.load(user_json)
        except ValidationError as err:
            return err.messages, 400

        # find user in database
        user = UserModel.find_by_username(user_data["username"])

        # check password
        if user and safe_str_cmp(user.password, user_data["password"]):
            # Black list all old refresh tokens before making new ones.
            BlacklistToken.revoke_all_old_refresh_tokens(user.id)

            # create access token
            access_token = create_access_token(identity=user.id, fresh=True)
            # create refresh token
            refresh_token = create_refresh_token(identity=user.id)

            # Lets store the tokens in the DB, as non-expired.
            new_access_token = BlacklistToken(access_token)
            new_refresh_token = BlacklistToken(refresh_token)

            new_access_token.save_to_db()
            new_refresh_token.save_to_db()

            return (
                {
                    "code": "login_success",
                    "message": USER_LOGIN_SUCCESSFULLY,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                200,
            )

        return {"error": TOKEN_AUTH_INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        user_id = get_jwt_identity()
        tokens = BlacklistToken.get_all_tokens_by_user_id(user_id)

        # Revoke all tokens that this user has.
        for token in tokens:
            token.revoke()

        return {"code": "logout_success", "message": USER_LOGOUT_SUCCESSFULLY}, 200
