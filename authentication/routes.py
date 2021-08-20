# flask packages
from flask_restful import Api

# project resources
from authentication.views import SignUpApi, VerifyUserApi, SocialLoginApi, EmailLoginApi, UserProfileApi, UserListApi, \
    UserProfileByIdApi


def create_authentication_routes(api: Api):
    """Adds resources to the api.

    :param api: Flask-RESTful Api Object

    :Example:

        api.add_resource(HelloWorld, '/', '/hello')
        api.add_resource(Foo, '/foo', endpoint="foo")
        api.add_resource(FooSpecial, '/special/foo', endpoint="foo")

    """
    api.add_resource(SignUpApi, '/api/auth/register-customer/')
    api.add_resource(EmailLoginApi, '/api/auth/login/')
    api.add_resource(SocialLoginApi, '/api/auth/social-login/')
    api.add_resource(VerifyUserApi, '/api/auth/verify-account/<uid>/<token>')
    api.add_resource(UserProfileApi, '/api/auth/user-profile/')
    api.add_resource(UserProfileByIdApi, '/api/auth/user-profile/<user_id>')
    api.add_resource(UserListApi, '/api/auth/user-list/')
