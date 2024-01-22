from django.db.utils import IntegrityError
from django.http import HttpResponse
from rest_framework.status import HTTP_400_BAD_REQUEST


class IntegrityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, IntegrityError):
            print(exception)
            print(exception.args)
            print(exception)
            return HttpResponse(
                content=str(exception),
                status=HTTP_400_BAD_REQUEST,
            )
