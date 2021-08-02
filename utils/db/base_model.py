from app import db
import datetime
import uuid
import mongoengine_goodjson as gj


class AbstractBaseModel(db.Document):
    # _id = UUIDField(db_field='id', primary_key=True, default=UUID, editable=False)
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())
    updated_at = db.DateTimeField(default=datetime.datetime.utcnow())

    meta = {
        'allow_inheritance': True,
        'abstract': True
    }
