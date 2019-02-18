from typing import List

from datetime import datetime

from flask_jwt_extended import decode_token

from restapi.db import db


def _epoch_utc_to_datetime(epoch_utc: str):
    return datetime.fromtimestamp(epoch_utc)


def _format_datetime(dt: datetime):
    return "{:02d}/{:02d}/{} {:02d}:{:02d}:{:02d}".format(
        dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second
    )


class BlacklistToken(db.Model):
    __tablename__ = "tokens"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.Integer, db.ForeignKey("users.id"))
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)

    user = db.relationship("UserModel", backref="tokens", lazy="select")

    @classmethod
    def create_new_token(cls, encoded_token: str) -> "BlacklistToken":
        decoded_token = decode_token(encoded_token)
        data_json = {
            "jti": decoded_token["jti"],
            "token_type": decoded_token["type"],
            "user_identity": decoded_token["identity"],
            "revoked": False,
            "expires": _epoch_utc_to_datetime(decoded_token["exp"]),
        }

        return BlacklistToken(**data_json)

    @classmethod
    def get_all_tokens_by_user_id(cls, user_id: int) -> List["BlacklistToken"]:
        return cls.query.filter_by(user_identity=user_id).all()

    @classmethod
    def is_token_revoked(cls, decoded_token: str) -> bool:
        db_token = cls.query.filter_by(jti=decoded_token["jti"]).first()

        if not db_token:
            return True

        return db_token.revoked

    @classmethod
    def revoke_all_old_refresh_tokens(cls, user_id: int) -> None:
        # get the user.
        tokens = cls.query.filter_by(
            token_type="refresh", user_identity=user_id, revoked=False
        ).all()

        for token in tokens:
            token.revoke()

    @classmethod
    def get_all(cls, filter_result: int = 10) -> List["BlacklistToken"]:
        return cls.query.limit(filter_result).all()

    def revoke(self) -> bool:
        self.revoked = True
        self.save_to_db()
        return True

    def unrevoke(self) -> bool:
        self.revoked = False
        self.save_to_db()
        return True

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
