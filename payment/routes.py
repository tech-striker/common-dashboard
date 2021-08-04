from flask_restful import Api

# project resources
from payment.views import CardApi, PaymentApi, RefundApi


def create_chat_routes(api: Api):
    """Adds resources to the api.

    :param api: Flask-RESTful Api Object

    :Example:

        api.add_resource(HelloWorld, '/', '/hello')
        api.add_resource(Foo, '/foo', endpoint="foo")
        api.add_resource(FooSpecial, '/special/foo', endpoint="foo")

    """
    api.add_resource(CardApi, '/card/')
    api.add_resource(PaymentApi, '/payment/')
    api.add_resource(RefundApi, '/refund/')
