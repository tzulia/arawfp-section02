from restapi.ma import ma
from restapi.models.store import StoreModel


class StoreSchema(ma.ModelSchema):
    items = ma.Nested("ItemSchema", many=True, only=['id', 'name', 'price'])

    class Meta:
        model = StoreModel
        dump_only = ("id",)
