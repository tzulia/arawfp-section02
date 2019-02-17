from ma import ma
from models.user import UserModel
from schemas.token_blacklist import BlacklistTokenSchema


class UserSchema(ma.ModelSchema):
    tokens = ma.Nested(BlacklistTokenSchema, many=True)

    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id", "is_admin")
        include_fk = True
