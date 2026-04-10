from django.conf import settings
from django_girosolution.__init__ import __version__

DJANGO_GIROSOLUTION_VERSION = __version__


class GIROSOLUTION_PAYMENT_METHODS:
    """
    girosolution payment methods
    """

    CC = 'CREDIT_CARD'
    PD = 'PAYDIREKT'
    GP = 'GIROPAY'
    PP = 'PAYPAL'
    WERO = 'WERO'
    PAYMENT_PAGE = 'PAYMENT_PAGE'


GIROSOLUTION_VALID_TRANSACTION_STATUSES = [4000]

GIROSOLUTION_API_BASE_URL = 'https://payment.girosolution.de/girocheckout/api/v2/'
GIROSOLUTION_API_URL = GIROSOLUTION_API_BASE_URL + 'transaction/start'
GIROSOLUTION_API_STATUS_URL = GIROSOLUTION_API_BASE_URL + 'transaction/status'
GIROSOLUTION_PAYPAGE_INIT_URL = GIROSOLUTION_API_BASE_URL + 'paypage/init'
GIROSOLUTION_PAYPAGE_PROJECTS_URL = GIROSOLUTION_API_BASE_URL + 'paypage/projects'

# checkout urls
GIROSOLUTION_RETURN_URL = getattr(settings, 'GIROSOLUTION_RETURN_URL', '/girosolution/return/')
GIROSOLUTION_SUCCESS_URL = getattr(settings, 'GIROSOLUTION_SUCCESS_URL', '/')
GIROSOLUTION_ERROR_URL = getattr(settings, 'GIROSOLUTION_ERROR_URL', '/')
GIROSOLUTION_CANCELLATION_URL = getattr(settings, 'GIROSOLUTION_CANCELLATION_URL', '/')
GIROSOLUTION_NOTIFICATION_URL = getattr(settings, 'GIROSOLUTION_NOTIFICATION_URL', '/girosolution/notify/')

# paypage urls
GIROSOLUTION_PAYPAGE_SUCCESS_URL = getattr(settings, 'GIROSOLUTION_PAYPAGE_SUCCESS_URL', '/')
GIROSOLUTION_PAYPAGE_FAIL_URL = getattr(settings, 'GIROSOLUTION_PAYPAGE_FAIL_URL', '/')
GIROSOLUTION_PAYPAGE_BACK_URL = getattr(settings, 'GIROSOLUTION_PAYPAGE_BACK_URL', '/')
GIROSOLUTION_PAYPAGE_NOTIFY_URL = getattr(settings, 'GIROSOLUTION_PAYPAGE_NOTIFY_URL', '/girosolution/paypage/notify/')

# paypage cache timeout in seconds
GIROSOLUTION_PAYPAGE_PROJECTS_CACHE_TIMEOUT = getattr(settings, 'GIROSOLUTION_PAYPAGE_PROJECTS_CACHE_TIMEOUT', 600)
