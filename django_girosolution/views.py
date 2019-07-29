import logging
from collections import OrderedDict

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, RedirectView

from django_girosolution.constants import RESULT_PAYMENT_STATUS
from django_girosolution.models import GirosolutionTransaction

from django_girosolution.wrappers import GirosolutionWrapper

import django_girosolution.wrappers as wrappers
from django_girosolution import settings as django_girosolution_settings

logger = logging.getLogger(__name__)


def validate_girosolution_get_params(girosolution_wrapper, get_params):
    desired_variables = ['gcReference', 'gcMerchantTxId', 'gcBackendTxId', 'gcAmount', 'gcCurrency', 'gcResultPayment', 'gcHash']

    # check for expected parameters
    if not all([var in get_params for var in desired_variables]):
        logger.error(
            _("Not all desired variables where part of the GiroSolution Notification. Payload: {}").format(str(get_params))
        )
        return False

    return True


class NotifyGirosolutionView(View):
    girosolution_wrapper = GirosolutionWrapper()

    def get(self, request, *args, **kwargs):

        get_params = OrderedDict()
        # creating OrderedDict out of query string, because we need it ordered for the hash check
        for query_param in request.META['QUERY_STRING'].split('&'):
            get_params[query_param.split('=')[0]] = "=".join(query_param.split('=')[1:])

        if not validate_girosolution_get_params(self.girosolution_wrapper, get_params):
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

    def handle_updated_transaction(self, girosolution_transaction, expected_statuses=django_girosolution_settings.GIROSOLUTION_VALID_TRANSACTION_STATUSES):
        """
            Override to use the girosolution_transaction in the way you want.
        """
        if girosolution_transaction.result_payment not in expected_statuses:
            logger.error(
                _("Girosolution Result faulty: {}").format(RESULT_PAYMENT_STATUS[girosolution_transaction.result_payment] if girosolution_transaction.result_payment in RESULT_PAYMENT_STATUS else girosolution_transaction.result_payment)
            )
            return HttpResponse(status=400)
        return HttpResponse(status=200)


class GirosolutionReturnView(RedirectView):
    girosolution_wrapper = wrappers

    def get_error_url(self):
        return django_girosolution_settings.GIROSOLUTION_ERROR_URL

    def get_cancel_url(self, girosolution_transaction):
        return girosolution_transaction.error_url

    def get_success_url(self, girosolution_transaction):
        return girosolution_transaction.success_url

    def get_redirect_url(self, *args, **kwargs):
        # creating OrderedDict out of query string, because we need it ordered for the hash check
        get_params = OrderedDict()
        for query_param in self.request.META['QUERY_STRING'].split('&'):
            get_params[query_param.split('=')[0]] = "=".join(query_param.split('=')[1:])

        if not validate_girosolution_get_params(self.girosolution_wrapper, get_params):
            return self.get_error_url()

        try:
            girosolution_transaction = GirosolutionTransaction.objects.get(reference=get_params['gcReference'])
        except GirosolutionTransaction.DoesNotExist:
            logger.error('girosolution transaction does not exist')
            return self.get_error_url()

        girosolution_transaction.result_payment = int(get_params['gcResultPayment'])
        girosolution_transaction.backend_tx_id = get_params['gcBackendTxId']
        girosolution_transaction.save()

        if girosolution_transaction.result_payment not in django_girosolution_settings.GIROSOLUTION_VALID_TRANSACTION_STATUSES:
            return self.get_cancel_url(girosolution_transaction)
        return self.get_success_url(girosolution_transaction)
