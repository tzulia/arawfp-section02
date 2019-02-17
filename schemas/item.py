from ma import ma
from models.item import ItemModel
from schemas.store import StoreSchema


class ItemSchema(ma.ModelSchema):
    store = ma.Nested(StoreSchema)

    class Meta:
        model = ItemModel
        dump_only = ("id",)
        include_fk = True
