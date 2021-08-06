from flask_restful import Api

# project resources
from payment.views import CardApi, PaymentApi, RefundApi, GenerateRefundApi, CancelRefundApi, StripeWebhookApi


def create_payment_routes(api: Api):
    """Adds resources to the api.

    :param api: Flask-RESTful Api Object

    :Example:

        api.add_resource(HelloWorld, '/', '/hello')
        api.add_resource(Foo, '/foo', endpoint="foo")
        api.add_resource(FooSpecial, '/special/foo', endpoint="foo")

    """
    api.add_resource(CardApi, '/api/payment/card/')
    api.add_resource(PaymentApi, '/api/payment/payment/')
    api.add_resource(RefundApi, '/api/payment/refund/')
    api.add_resource(GenerateRefundApi, '/api/payment/generate-refund/<payment_id>')
    api.add_resource(CancelRefundApi, '/api/payment/cancel-refund/')
    api.add_resource(StripeWebhookApi, '/api/payment/stripe-webhook/')
