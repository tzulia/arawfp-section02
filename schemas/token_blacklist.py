from ma import ma
from models.token_blacklist import BlacklistToken


class BlacklistTokenSchema(ma.ModelSchema):
    class Meta:
        model = BlacklistToken
        load_only = ("jti",)
        dump_only = ("id",)
