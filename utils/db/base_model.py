from mongoengine import Document, DateTimeField, UUIDField
import datetime
import uuid


class AbstractBaseModel(Document):
    id = UUIDField(db_field='id', primary_key=True, default=uuid.uuid4, editable=False)
    created_at = DateTimeField(default=datetime.datetime.utcnow())
    updated_at = DateTimeField(default=datetime.datetime.utcnow())

    meta = {
        'allow_inheritance': True,
        'abstract': True
    }
