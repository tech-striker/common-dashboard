from app import db
from utils.constants import *
from utils.db.base_model import AbstractBaseModel
from authentication.models import UserLoginInfo
from utils.constants import DEFAULT_PAYMENT_STATUS_TYPE, DEFAULT_REFUND_STATUS_TYPE, REFUND_STATUS_TYPES, \
    PAYMENT_STATUS_TYPES


class PaymentCustomerModel(AbstractBaseModel):
    user = db.ReferenceField(UserLoginInfo, required=True)
    customer_id = db.StringField(required=True)

    def to_json(self, *args, **kwargs):
        return {
            "id": str(self.pk),
            "user": self.user.to_json()
        }


class CardModel(AbstractBaseModel):
    user = db.ReferenceField(UserLoginInfo, required=True)
    last_4 = db.StringField(length=4, required=True)
    stripe_card_id = db.StringField(required=True)
    card_type = db.StringField(required=True)
    is_primary = db.BooleanField(default=False)

    def to_json(self, *args, **kwargs):
        return {
            "id": str(self.pk),
            "user": str(self.user),
            "last_4": self.last_4,
            "stripe_card_id": self.stripe_card_id,
            "card_type": self.card_type,
            "is_primary": self.is_primary,
            "created_at": self.created_at
        }


class PaymentModel(AbstractBaseModel):
    user = db.ReferenceField(UserLoginInfo, required=True)
    order = db.StringField(required=True)
    card = db.ReferenceField(CardModel)
    payment_id = db.StringField(required=True)
    amount = db.IntField(required=True)
    currency = db.StringField(default='USD')
    status = db.StringField(choices=PAYMENT_STATUS_TYPES, required=True, default=DEFAULT_PAYMENT_STATUS_TYPE)

    def to_json(self, *args, **kwargs):
        return {
            "id": str(self.pk),
            "order": self.order,
            "user": str(self.user),
            "card": self.card.to_json(),
            "payment_id": self.payment_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "created_at": self.created_at
        }


class RefundModel(AbstractBaseModel):
    payment = db.ReferenceField(PaymentModel)
    status = db.StringField(choices=REFUND_STATUS_TYPES, default=DEFAULT_REFUND_STATUS_TYPE, required=True)
    refund_reason = db.StringField(default='')
    refund_cancellation_reason = db.StringField(default='')
    refund_date = db.DateTimeField(required=False)

    def to_json(self):
        return {
            "id": str(self.pk),
            'payment': self.payment.to_json(),
            'status': self.status,
            'refund_date': self.refund_date,
            'refund_reason': self.refund_reason,
            'refund_cancellation_reason': self.refund_cancellation_reason,
            "created_at": self.created_at
        }
