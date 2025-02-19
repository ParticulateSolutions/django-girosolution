import logging
import requests
from collections import OrderedDict
from django.utils.translation import gettext_lazy as _

from django_girosolution.constants import SHOPPING_CART_TYPE
from django_girosolution.settings import *

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

    def start_transaction(self, merchant_tx_id, amount, purpose,
                          currency='EUR',
                          redirect_url=GIROSOLUTION_RETURN_URL,
                          notify_url=GIROSOLUTION_NOTIFICATION_URL,
                          success_url=GIROSOLUTION_SUCCESS_URL,
                          error_url=GIROSOLUTION_ERROR_URL,
                          shipping_address=None,
                          shoppingCartType=SHOPPING_CART_TYPE.ANONYMOUS_DONATION,
                          merchantOrderReferenceNumber=False,
                          kassenzeichen=False):
        """
        girosolution transaction. The data needs to be ordered like in the API docs, otherwise the hash will be invalid.
        :param merchant_tx_id:
        :param amount:
        :param purpose:
        :param currency:
        :param redirect_url:
        :param notify_url:
        :param success_url:
        :param error_url:
        :param shipping_address: None or dict that contains all fields that start with "shipping". Content depends on shoppingCartType.
        :param shoppingCartType: For Giropay. Default "ANONYMOUS_DONATION" because it requires no shipping_address. Other values require other shipping_address fields. See their docs.
        :param merchantOrderReferenceNumber: For Giropay. str with max len 20
        :param kassenzeichen: For Giropay. str with max len 255. Should be visible in girocockpit and will be in export.
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

        elif self.payment_type is GIROSOLUTION_PAYMENT_METHODS.GP:
            # go with giropay
            data = OrderedDict()
            data['merchantId'] = self.payment.get('MERCHANT_ID')
            data['projectId'] = self.payment.get('PROJECT_ID')
            data['merchantTxId'] = merchant_tx_id
            data['amount'] = amount
            data['currency'] = currency
            data['purpose'] = purpose
            data['shoppingCartType'] = shoppingCartType
            if shipping_address:
                data['shippingAddresseFirstName'] = shipping_address.get('shippingAddresseFirstName', '')
                data['shippingAddresseLastName'] = shipping_address.get('shippingAddresseLastName', '')
                data['shippingCompany'] = shipping_address.get('shippingCompany', '')
                data['shippingAdditionalAddressInformation'] = shipping_address.get('shippingAdditionalAddressInformation', '')
                data['shippingStreet'] = shipping_address.get('shippingStreet', '')
                data['shippingStreetNumber'] = shipping_address.get('shippingStreetNumber', '')
                data['shippingZipCode'] = shipping_address.get('shippingZipCode', '')
                data['shippingCity'] = shipping_address.get('shippingCity', '')
                data['shippingCountry'] = shipping_address.get('shippingCountry', '')
                data['shippingEmail'] = shipping_address.get('shippingEmail', '')
            if merchantOrderReferenceNumber:
                data['merchantOrderReferenceNumber'] = merchantOrderReferenceNumber
            data['urlRedirect'] = redirect_url
            data['urlNotify'] = notify_url
            if kassenzeichen:
                data['kassenzeichen'] = kassenzeichen

        elif self.payment_type is GIROSOLUTION_PAYMENT_METHODS.PP:
            # go with paypal
            data = OrderedDict()
            data['merchantId'] = self.payment.get('MERCHANT_ID')
            data['projectId'] = self.payment.get('PROJECT_ID')
            data['merchantTxId'] = merchant_tx_id
            data['amount'] = amount
            data['currency'] = currency
            data['purpose'] = purpose
            data['urlRedirect'] = redirect_url
            data['urlNotify'] = notify_url

        elif self.payment_type is GIROSOLUTION_PAYMENT_METHODS.PD:
            # go with paydirekt
            data = OrderedDict()
            data['merchantId'] = self.payment.get('MERCHANT_ID')
            data['projectId'] = self.payment.get('PROJECT_ID')
            data['merchantTxId'] = merchant_tx_id
            data['amount'] = amount
            data['currency'] = currency
            data['purpose'] = purpose
            data['shippingAddresseFirstName'] = shipping_address['shippingAddresseFirstName']
            data['shippingAddresseLastName'] = shipping_address['shippingAddresseLastName']
            data['shippingZipCode'] = shipping_address['shippingZipCode']
            data['shippingCity'] = shipping_address['shippingCity']
            data['shippingCountry'] = shipping_address['shippingCountry']
            data['orderId'] = merchant_tx_id
            data['urlRedirect'] = redirect_url
            data['urlNotify'] = notify_url

        else:
            raise Exception(_("unknown payment method"))

        # make api call with given data
        response = self.call_api(url=GIROSOLUTION_API_URL, data=data)

        response_hash = response.headers.get('hash')
        response_dict = response.json()
        response_text = response.text

        generated_hash = self._generate_hash_from_text(response_text)
        # check if hash is valid
        assert response_hash == generated_hash, _("Response hash {} not compatible with the generated hash {}.").format(response_hash, generated_hash)

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
            logger.error(_("no reference given by response"))
            return None
        return response_dict

    def update_transaction_state(self, girosolution_transaction) -> bool:
        """

        :param girosolution: GirosolutionTransaction
        :return: bool; True if state is successfully updated
        """
        data = OrderedDict()
        data['merchantId'] = girosolution_transaction.merchant_id
        data['projectId'] = girosolution_transaction.project_id
        data['reference'] = girosolution_transaction.reference
        response = self.call_api(url=GIROSOLUTION_API_STATUS_URL, data=data)
        response_hash = response.headers.get('hash')
        response_dict = response.json()
        response_text = response.text

        generated_hash = self._generate_hash_from_text(response_text)
        # check if hash is valid
        assert response_hash == generated_hash, _("Response hash {} not compatible with the generated hash {}.").format(response_hash, generated_hash)

        update_fields = ["latest_response_code", "latest_response_msg"]
        girosolution_transaction.latest_response_code = response_dict.get('rc')
        girosolution_transaction.latest_response_msg = response_dict.get('msg')
        if response_dict.get('rc') == 0:
            update_fields += ["backend_tx_id", "result_payment", "result_avs", "obv_name",]
            girosolution_transaction.backend_tx_id = response_dict.get('backendTxId', None)
            girosolution_transaction.result_payment = int(response_dict.get('resultPayment', None))
            girosolution_transaction.result_avs = int(response_dict.get('resultAVS', None))
            girosolution_transaction.obv_name = response_dict.get('obvName', None)
        girosolution_transaction.save(update_fields=update_fields)

        return response_dict.get('rc') == 0

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
