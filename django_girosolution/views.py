import logging
from collections import OrderedDict

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, RedirectView

from django_girosolution.constants import RESULT_PAYMENT_STATUS
from django_girosolution.models import GirosolutionTransaction

from django_girosolution.wrappers import GirosolutionWrapper

import django_girosolution.wrappers as wrappers
from django_girosolution import settings as django_girosolution_settings

logger = logging.getLogger(__name__)


def parse_query_string(query_string):
    """Parse a query string into an OrderedDict, preserving parameter order for hash verification."""
    params = OrderedDict()
    for query_param in query_string.split('&'):
        key, _, value = query_param.partition('=')
        params[key] = value
    return params


def validate_girosolution_params(girosolution_wrapper: GirosolutionWrapper, params):
    desired_variables = [
        'gcReference',
        'gcMerchantTxId',
        'gcBackendTxId',
        'gcAmount',
        'gcCurrency',
        'gcResultPayment',
        'gcHash',
    ]

    # check for expected parameters
    if not all([var in params for var in desired_variables]):
        logger.error(_(f'Not all desired variables were part of the GiroSolution Notification. Payload: {params}'))
        return False

    if not girosolution_wrapper.validate_hash(params, params['gcHash']):
        logger.error(_('GiroSolution hash validation failed'))
        return False

    return True


class NotifyGirosolutionView(View):
    girosolution_wrapper = GirosolutionWrapper()

    def get(self, request, *args, **kwargs):
        get_params = parse_query_string(request.META['QUERY_STRING'])

        if not validate_girosolution_params(self.girosolution_wrapper, get_params):
            return HttpResponse(status=400)

        try:
            girosolution_transaction = GirosolutionTransaction.objects.get(reference=get_params['gcReference'])
        except GirosolutionTransaction.DoesNotExist:
            return HttpResponse(status=400)

        girosolution_transaction.result_payment = int(get_params['gcResultPayment'])
        girosolution_transaction.backend_tx_id = get_params['gcBackendTxId']
        girosolution_transaction.save()

        return self.handle_updated_transaction(girosolution_transaction=girosolution_transaction)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(NotifyGirosolutionView, self).dispatch(request, *args, **kwargs)

    def handle_updated_transaction(
        self,
        girosolution_transaction,
        expected_statuses=django_girosolution_settings.GIROSOLUTION_VALID_TRANSACTION_STATUSES,
    ):
        """
        Override to use the girosolution_transaction in the way you want.
        """
        if girosolution_transaction.result_payment not in expected_statuses:
            logger.error(
                _('Girosolution Result faulty: {}').format(
                    RESULT_PAYMENT_STATUS[girosolution_transaction.result_payment]
                    if girosolution_transaction.result_payment in RESULT_PAYMENT_STATUS
                    else girosolution_transaction.result_payment
                )
            )
            return HttpResponse(status=400)
        return HttpResponse(status=200)


class NotifyPaypageView(View):
    """
    Handles server-to-server notifications from GiroCheckout Payment Page.
    The paypage notification is sent as GET with gc* parameters including
    gcPaymethod and gcType in addition to the standard parameters.
    Override handle_updated_transaction() for custom logic.
    """

    girosolution_wrapper = GirosolutionWrapper()

    def get(self, request, *args, **kwargs):
        get_params = parse_query_string(request.META['QUERY_STRING'])

        if not validate_girosolution_params(self.girosolution_wrapper, get_params):
            return HttpResponse(status=400)

        try:
            girosolution_transaction = GirosolutionTransaction.objects.get(reference=get_params['gcReference'])
        except GirosolutionTransaction.DoesNotExist:
            return HttpResponse(status=400)

        girosolution_transaction.result_payment = int(get_params['gcResultPayment'])
        girosolution_transaction.backend_tx_id = get_params['gcBackendTxId']
        girosolution_transaction.save()

        return self.handle_updated_transaction(girosolution_transaction=girosolution_transaction)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(NotifyPaypageView, self).dispatch(request, *args, **kwargs)

    def handle_updated_transaction(
        self,
        girosolution_transaction,
        expected_statuses=django_girosolution_settings.GIROSOLUTION_VALID_TRANSACTION_STATUSES,
    ):
        """
        Override to use the girosolution_transaction in the way you want.
        """
        if girosolution_transaction.result_payment not in expected_statuses:
            logger.error(
                _('Girosolution Paypage Result faulty: {}').format(
                    RESULT_PAYMENT_STATUS[girosolution_transaction.result_payment]
                    if girosolution_transaction.result_payment in RESULT_PAYMENT_STATUS
                    else girosolution_transaction.result_payment
                )
            )
            return HttpResponse(status=400)
        return HttpResponse(status=200)


class PaypageReturnView(RedirectView):
    """
    Handles the redirect back from GiroCheckout Payment Page.
    The paypage sends results via POST to successUrl/failUrl.
    """

    girosolution_wrapper = GirosolutionWrapper()

    def get_error_url(self):
        return django_girosolution_settings.GIROSOLUTION_ERROR_URL

    def get_cancel_url(self, girosolution_transaction):
        return girosolution_transaction.error_url

    def get_success_url(self, girosolution_transaction):
        return girosolution_transaction.success_url

    def post(self, request, *args, **kwargs):
        post_params = request.POST.dict()

        if not validate_girosolution_params(self.girosolution_wrapper, post_params):
            return HttpResponseRedirect(self.get_error_url())

        try:
            girosolution_transaction = GirosolutionTransaction.objects.get(reference=post_params['gcReference'])
        except GirosolutionTransaction.DoesNotExist:
            logger.error('girosolution paypage transaction does not exist')
            return HttpResponseRedirect(self.get_error_url())

        girosolution_transaction.result_payment = int(post_params['gcResultPayment'])
        girosolution_transaction.backend_tx_id = post_params['gcBackendTxId']
        girosolution_transaction.save()

        if not girosolution_transaction.valid_payment:
            return HttpResponseRedirect(self.get_cancel_url(girosolution_transaction))
        return HttpResponseRedirect(self.get_success_url(girosolution_transaction))

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(PaypageReturnView, self).dispatch(request, *args, **kwargs)


class GirosolutionReturnView(RedirectView):
    girosolution_wrapper = GirosolutionWrapper()

    def get_error_url(self):
        return django_girosolution_settings.GIROSOLUTION_ERROR_URL

    def get_cancel_url(self, girosolution_transaction):
        return girosolution_transaction.error_url

    def get_success_url(self, girosolution_transaction):
        return girosolution_transaction.success_url

    def get_redirect_url(self, *args, **kwargs):
        get_params = parse_query_string(self.request.META['QUERY_STRING'])

        if not validate_girosolution_params(self.girosolution_wrapper, get_params):
            return self.get_error_url()

        try:
            girosolution_transaction = GirosolutionTransaction.objects.get(reference=get_params['gcReference'])
        except GirosolutionTransaction.DoesNotExist:
            logger.error('girosolution transaction does not exist')
            return self.get_error_url()

        girosolution_transaction.result_payment = int(get_params['gcResultPayment'])
        girosolution_transaction.backend_tx_id = get_params['gcBackendTxId']
        girosolution_transaction.save()

        if not girosolution_transaction.valid_payment:
            return self.get_cancel_url(girosolution_transaction)
        return self.get_success_url(girosolution_transaction)
