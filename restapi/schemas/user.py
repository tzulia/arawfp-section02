from restapi.ma import ma
from restapi.models.user import UserModel
from .token_blacklist import BlacklistTokenSchema


class UserSchema(ma.ModelSchema):
    tokens = ma.Nested(BlacklistTokenSchema, many=True)

    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id", "is_admin")
        include_fk = True
