import requests
from django_girosolution.settings import *
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class GirosolutionWrapper(object):
    """
    girosolution girocheckout integration
    """
    interface_version = 'django_girosolution_v{}'.format(DJANGO_GIROSOLUTION_VERSION)

    api_url = None
    transaction_start_url = None
    external_payment_url = None

    issuer_url = None

    payment = None
    payment_type = None

    def __init__(self, payment=None):
        """
        initial
        :param payment: object with auth and paymenttype should contain PROJECT_ID, TYPE, PROJECT_PASSWORD, MERCHANT_ID
        """
        super(GirosolutionWrapper, self).__init__()

        try:
            if payment:
                self.payment = payment
                self.payment_type = self.payment.get('TYPE')
            else:
                return None
        except:
            pass


    def _get_hash_for_payload(self, payload):
        """
        generates hash for girosolution requests
        :param payload:
        :return: string
        """
        return ''.join(map(str, [value for value in payload.values()]))


    def _generate_hash_from_dict(self, data_dict):
        """
        generates hash for api call
        :param data_dict:
        :return:
        """
        import hashlib
        import hmac
        data_string = "".join([str(val) for val in data_dict.values()])
        data_hash = hmac.new(self.payment['PROJECT_PASSWORD'], "{}".format(data_string).encode("utf-8"),
                             hashlib.md5).hexdigest()
        return data_hash

    def _generate_hash_from_text(self, data_text):
        """
        gerenerates hash for response object text
        :param data_text:
        :return:
        """
        import hashlib
        import hmac
        data_hash = hmac.new(self.payment['PROJECT_PASSWORD'], data_text.encode("utf-8"), hashlib.md5).hexdigest()
        return data_hash

    def _check_transaction_state(self):
        """
        check if transaction was successful and payment is done
        :return: bool
        """

        return True

    def start_transaction(self, merchant_tx_id, amount, purpose,
        currency='EUR',
        redirect_url=GIROSOLUTION_RETURN_URL,
        notify_url=GIROSOLUTION_NOTIFICATION_URL,
        success_url=GIROSOLUTION_SUCCESS_URL,
        error_url=GIROSOLUTION_ERROR_URL):
        """
        girosolution transaction
        :param merchant_tx_id:
        :param amount:
        :param purpose:
        :param currency:
        :param redirect_url:
        :param notify_url:
        :param success_url:
        :param error_url:
        :return: response dict from girocheckout
        """

        # check type to start
        if self.payment_type is GIROSOLUTION_PAYMENT_METHODS.CC:

            # go with creditcard
            data = OrderedDict()
            data['merchantId'] = self.payment.get('MERCHANT_ID')
            data['projectId'] = self.payment.get('PROJECT_ID')
            data['merchantTxId'] = merchant_tx_id
            data['amount'] = amount
            data['currency'] = currency
            data['purpose'] = purpose
            data['urlRedirect'] = redirect_url
            data['urlNotify'] = notify_url

        #
        #
        # todo: add datamapping for other paymentmethods

        else:
            logger.error(_("unknown payment method"))


        # make api call with given data
        response = self.call_api(url=GIROSOLUTION_API_URL, data=data)

        response_hash = response.headers.get('hash')
        response_dict = response.json()
        response_text = response.text

        generated_hash = self._generate_hash_from_text(response_text)
        # check if hash is valid
        if response_hash != generated_hash:
            logger.error(_("Response hash {} not compatible with the generated hash {}.").format(response_hash,
                                                                                                 generated_hash))

        # todo: errorhandling
        if response_dict.get('reference'):
            # generate transaction object
            from django_girosolution.models import GirosolutionTransaction
            g_tx = GirosolutionTransaction()
            g_tx.redirect_url = redirect_url
            g_tx.notify_url = notify_url
            g_tx.success_url = success_url
            g_tx.error_url = error_url
            g_tx.project_id = self.payment.get('PROJECT_ID')
            g_tx.merchant_id = self.payment.get('MERCHANT_ID')
            g_tx.merchant_tx_id = merchant_tx_id
            g_tx.amount = amount
            g_tx.currency = currency
            g_tx.latest_response_code = response_dict.get('rc')
            g_tx.purpose = purpose
            g_tx.reference = response_dict.get('reference')
            g_tx.payment_type = self.payment_type
            g_tx.save()
        else:
            return None

        return response_dict

    def call_api(self, url=None, data=None):
        """
        call girosolution api
        :param url: http url of api endpoint
        :param data: dataobject as OrderedDict
        :return: response object
        """

        if not self.payment:
            return False
        if not url.lower().startswith('http'):
            url = '{0}{1}'.format(self.api_url, url)

        generated_hash = self._generate_hash_from_dict(data)
        data.update({'hash': generated_hash})

        try:
            response = requests.post(url, data=data)
        except requests.HTTPError as e:
            logger = logging.getLogger(__name__)
            if hasattr(e, 'errno'):
                logger.error("Girosolution Error {0}({1})".format(e.errno, e.strerror))
            else:
                logger.error(
                    "Girosolution Error({0})".format(e.strerror))
        else:
            return response
        return False
