from django.conf import settings
from django_girosolution.__init__ import __version__

DJANGO_GIROSOLUTION_VERSION = __version__


class GIROSOLUTION_PAYMENT_METHODS:
    """
    girosolution payment methods
    """
    CC = 'CREDIT_CARD'
    PD = 'PAYDIREKT'


GIROSOLUTION_VALID_TRANSACTION_STATUSES = [4000]

GIROSOLUTION_API_URL = 'https://payment.girosolution.de/girocheckout/api/v2/transaction/start'

# checkout urls
GIROSOLUTION_RETURN_URL = getattr(settings, 'GIROSOLUTION_RETURN_URL', '/girosolution/return/')
GIROSOLUTION_SUCCESS_URL = getattr(settings, 'GIROSOLUTION_SUCCESS_URL', '/')
GIROSOLUTION_ERROR_URL = getattr(settings, 'GIROSOLUTION_ERROR_URL', '/')
GIROSOLUTION_CANCELLATION_URL = getattr(settings, 'GIROSOLUTION_CANCELLATION_URL', '/')
GIROSOLUTION_NOTIFICATION_URL = getattr(settings, 'GIROSOLUTION_NOTIFICATION_URL', '/girosolution/notify/')

