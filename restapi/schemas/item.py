from restapi.ma import ma
from restapi.models.item import ItemModel


class ItemSchema(ma.ModelSchema):
    store = ma.Nested("StoreSchema", only=['name', 'id'])         # I want this.

    class Meta:
        model = ItemModel
        load_only = ("store_id",)
        dump_only = ("id",)
        include_fk = True
