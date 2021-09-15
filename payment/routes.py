from flask_restful import Api

# project resources
from payment.views import StripeCardApi, StripePaymentApi, RefundApi, StripeGenerateRefundApi, CancelRefundApi, \
    StripeWebhookApi, InvoiceApi, RazorpayPaymentApi, RazorpayCapturePaymentApi, RazorpayGenerateRefundApi, \
    RazorpayWebhookApi, ShippingAddressApi


def create_payment_routes(api: Api):
    """Adds resources to the api.

    :param api: Flask-RESTful Api Object

    :Example:

        api.add_resource(HelloWorld, '/', '/hello')
        api.add_resource(Foo, '/foo', endpoint="foo")
        api.add_resource(FooSpecial, '/special/foo', endpoint="foo")

    """

    # STRIPE ROUTES
    api.add_resource(StripeCardApi, '/api/payment/stripe/card/')
    api.add_resource(StripePaymentApi, '/api/payment/stripe/payment/')
    api.add_resource(StripeGenerateRefundApi, '/api/payment/stripe/generate-refund/<payment_id>')

    # RAZORPAY ROUTES
    api.add_resource(RazorpayPaymentApi, '/api/payment/razorpay/payment/')
    api.add_resource(RazorpayCapturePaymentApi, '/api/payment/razorpay/capture-payment/')
    api.add_resource(RazorpayGenerateRefundApi, '/api/payment/razorpay/generate-refund/<payment_id>')

    # WEBHOOKS
    api.add_resource(StripeWebhookApi, '/api/payment/stripe-webhook/')
    api.add_resource(RazorpayWebhookApi, '/api/payment/razorpay-webhook/')

    # COMMON
    api.add_resource(RefundApi, '/api/payment/refund/')
    api.add_resource(CancelRefundApi, '/api/payment/cancel-refund/')
    api.add_resource(InvoiceApi, '/api/payment/get-invoices/')

    # LOCATIONS
    api.add_resource(ShippingAddressApi, '/api/payment/shipping-address/')

