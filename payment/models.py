from app import db
from utils.constants import *
from utils.db.base_model import AbstractBaseModel
from authentication.models import UserLoginInfo


class PaymentCustomer(AbstractBaseModel):
    user = db.ReferenceField(UserLoginInfo, required=True)
    customer_id = db.StringField(required=True)

    def to_json(self, *args, **kwargs):
        return {
            "id": str(self.pk),
            "user": self.user.to_json()
        }


class Card(AbstractBaseModel):
    user = db.ReferenceField(UserLoginInfo, required=True)
    last_4 = db.StringField(length=4, required=True)
    stripe_card_id = db.StringField(required=True)
    card_type = db.StringField(required=True)
    is_primary = db.BooleanField(default=False)

    def to_json(self, *args, **kwargs):
        return {
            "id": str(self.pk),
            "user": self.user.to_json(),
            "last_4": self.last_4,
            "stripe_card_id": self.stripe_card_id,
            "card_type": self.card_type,
            "is_primary": self.is_primary
        }


class Payment(AbstractBaseModel):
    user = db.ReferenceField(UserLoginInfo, required=True)
    order = db.StringField(required=True)
    card = db.ReferenceField(Card)
    payment_id = db.StringField(required=True)
    charge_id = db.StringField(required=True)
    amount = db.IntField(required=True)
    currency = db.StringField(default='USD')
    status = db.StringField(required=True, default='INITIATED')

    def to_json(self, *args, **kwargs):
        return {
            "id": str(self.pk),
            "order": self.order,
            "user": self.user.to_json(),
            "card": self.card.to_json(),
            "payment_id": self.payment_id,
            "charge_id": self.charge_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status
        }
