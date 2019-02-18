from typing import Dict, List, Tuple
from functools import wraps

from restapi.db import db
from flask_jwt_extended import get_jwt_identity


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_all(cls) -> List["UserModel"]:
        return cls.query.all()

    def save_to_db(self) -> Tuple[Dict, int]:
        if self.username and self.password:
            db.session.add(self)
            db.session.commit()
            return {"message": "Saved"}, 200
        else:
            return {"error": "Please input username/password"}, 400

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    # @require_admin decorator
    def require_admin(func):
        @wraps(func)
        def function_that_runs_func(*args, **kwargs):
            user_id = get_jwt_identity()
            if user_id:
                user = UserModel.find_by_id(user_id)
                if user and user.is_admin:
                    return func(*args, **kwargs)
            return {"error": "Invalid Credentials"}, 401

        return function_that_runs_func
