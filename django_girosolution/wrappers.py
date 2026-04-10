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
        elif self.payment_type is GIROSOLUTION_PAYMENT_METHODS.WERO:
            data = OrderedDict()
            data["merchantId"] = self.payment.get("MERCHANT_ID")
            data["projectId"] = self.payment.get("PROJECT_ID")
            data["merchantTxId"] = merchant_tx_id
            data["amount"] = amount
            data["currency"] = currency
            data["purpose"] = purpose
            data["urlRedirect"] = redirect_url
            data["urlNotify"] = notify_url
            if kassenzeichen:
                data['kassenzeichen'] = kassenzeichen
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

    def get_paypage_projects(self):
        """
        Fetch available payment methods/projects for the paypage.
        Results are cached using Django's cache framework.
        :return: list of project dicts with keys: id, name, paymethod, mode
        """
        from django.core.cache import cache

        cache_key = 'girosolution_paypage_projects_{}_{}'.format(
            self.payment['MERCHANT_ID'], self.payment['PROJECT_ID']
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        data = OrderedDict()
        data['merchantId'] = self.payment.get('MERCHANT_ID')
        data['projectId'] = self.payment.get('PROJECT_ID')

        response = self.call_api(url=GIROSOLUTION_PAYPAGE_PROJECTS_URL, data=data)
        if not response:
            return None

        response_hash = response.headers.get('hash')
        response_text = response.text
        generated_hash = self._generate_hash_from_text(response_text)
        assert response_hash == generated_hash, _(
            "Response hash {} not compatible with the generated hash {}.").format(response_hash, generated_hash)

        response_dict = response.json()
        if response_dict.get('rc') != 0:
            logger.error(_("Paypage projects request failed: {}").format(response_dict.get('msg')))
            return None

        projects = response_dict.get('projects', [])
        cache.set(cache_key, projects, GIROSOLUTION_PAYPAGE_PROJECTS_CACHE_TIMEOUT)
        return projects

    def init_paypage(self,
                     merchant_tx_id,
                     amount,
                     purpose,
                     currency='EUR',
                     test=0,
                     success_url=GIROSOLUTION_PAYPAGE_SUCCESS_URL,
                     fail_url=GIROSOLUTION_PAYPAGE_FAIL_URL,
                     back_url=GIROSOLUTION_PAYPAGE_BACK_URL,
                     notify_url=GIROSOLUTION_PAYPAGE_NOTIFY_URL,
                     error_url=GIROSOLUTION_ERROR_URL,
                     pagetype=None,
                     locale=None,
                     description=None,
                     paymethods=None,
                     payprojects=None,
                     transaction_type=None,
                     single=None,
                     timeout=None,
                     expirydate=None,
                     organization=None,
                     freeamount=None,
                     fixedvalues=None,
                     minamount=None,
                     maxamount=None,
                     projectlist=None,
                     pkn=None,
                     certdata=None,
                     otherpayments=None,
                     kassenzeichen=None,
                     qrcodeReturn=None,
                     informationText=None,
                     tds2Address=None,
                     tds2Postcode=None,
                     tds2City=None,
                     tds2Country=None,
                     tds2Optional=None,
                     mandateReference=None,
                     mandateSignedOn=None,
                     mandateReceiverName=None,
                     mandateSequence=None,
                     billingAddress=None,
                     shippingAddress=None,
                     customerInfo=None,
                     basket=None):
        """
        Initialize a GiroCheckout Payment Page.
        Field order in the OrderedDict matters for hash computation.
        :param merchant_tx_id: unique transaction id
        :param amount: amount in cents
        :param purpose: purpose text (max 50 chars)
        :param currency: ISO 4217 currency code
        :param test: 1 for test mode, 0 for live
        :param success_url: redirect URL on successful payment
        :param fail_url: redirect URL on failed payment
        :param back_url: redirect URL when user clicks back
        :param notify_url: server-to-server notification URL
        :param error_url: stored on the transaction for app-level error handling
        :param pagetype: 0=API-Paypage, 1=Payment page, 2=Donation page
        :param locale: 'de' or 'en'
        :param description: description shown on payment page (max 120 chars)
        :param paymethods: comma-separated payment method codes
        :param payprojects: comma-separated project IDs
        :param transaction_type: 'SALE' or 'AUTH'
        :param single: 0=reusable, 1=one attempt, 2=one successful payment
        :param timeout: timeout in seconds for payment method selection
        :param expirydate: expiration date YYYY-MM-DD
        :param organization: organization name (max 70 chars)
        :param freeamount: 1=free amount entry
        :param fixedvalues: JSON string of amount options e.g. '["10000","20000"]'
        :param minamount: min amount in cents if freeamount=1
        :param maxamount: max amount in cents if freeamount=1
        :param projectlist: JSON string of project names for donation pages
        :param pkn: 'create' to generate pseudo card number
        :param certdata: 1=offer donation certificate form
        :param otherpayments: JSON string of external payment methods
        :param kassenzeichen: additional reference for GiroCockpit
        :param qrcodeReturn: 1-20 to generate QR code
        :param informationText: info text displayed on payment page (max 300 chars)
        :param tds2Address: 3DS2 billing address
        :param tds2Postcode: 3DS2 postal code
        :param tds2City: 3DS2 city
        :param tds2Country: 3DS2 country ISO
        :param tds2Optional: 3DS2 optional fields JSON string
        :param mandateReference: SEPA mandate reference
        :param mandateSignedOn: SEPA mandate date
        :param mandateReceiverName: SEPA mandate receiver
        :param mandateSequence: 1=single, 2=first, 3=recurring, 4=last
        :param billingAddress: JSON string for Klarna/Apple Pay/Google Pay
        :param shippingAddress: JSON string for Klarna/Apple Pay/Google Pay
        :param customerInfo: JSON string for Klarna/Apple Pay/Google Pay
        :param basket: JSON string shopping cart for Klarna/Apple Pay/Google Pay
        :return: response dict from girocheckout with 'reference' and 'url' keys
        """
        # Build OrderedDict in the exact order specified by the API docs (hash depends on order)
        data = OrderedDict()
        data['merchantId'] = self.payment.get('MERCHANT_ID')
        data['projectId'] = self.payment.get('PROJECT_ID')
        data['merchantTxId'] = merchant_tx_id
        data['amount'] = amount
        data['currency'] = currency
        data['purpose'] = purpose
        if description is not None:
            data['description'] = description
        if pagetype is not None:
            data['pagetype'] = pagetype
        if expirydate is not None:
            data['expirydate'] = expirydate
        if single is not None:
            data['single'] = single
        if timeout is not None:
            data['timeout'] = timeout
        if transaction_type is not None:
            data['type'] = transaction_type
        if locale is not None:
            data['locale'] = locale
        if paymethods is not None:
            data['paymethods'] = paymethods
        if payprojects is not None:
            data['payprojects'] = payprojects
        if organization is not None:
            data['organization'] = organization
        if freeamount is not None:
            data['freeamount'] = freeamount
        if fixedvalues is not None:
            data['fixedvalues'] = fixedvalues
        if minamount is not None:
            data['minamount'] = minamount
        if maxamount is not None:
            data['maxamount'] = maxamount
        if projectlist is not None:
            data['projectlist'] = projectlist
        if pkn is not None:
            data['pkn'] = pkn
        data['test'] = test
        if certdata is not None:
            data['certdata'] = certdata
        if otherpayments is not None:
            data['otherpayments'] = otherpayments
        data['successUrl'] = success_url
        data['backUrl'] = back_url
        data['failUrl'] = fail_url
        data['notifyUrl'] = notify_url
        if tds2Address is not None:
            data['tds2Address'] = tds2Address
        if tds2Postcode is not None:
            data['tds2Postcode'] = tds2Postcode
        if tds2City is not None:
            data['tds2City'] = tds2City
        if tds2Country is not None:
            data['tds2Country'] = tds2Country
        if tds2Optional is not None:
            data['tds2Optional'] = tds2Optional
        if mandateReference is not None:
            data['mandateReference'] = mandateReference
        if mandateSignedOn is not None:
            data['mandateSignedOn'] = mandateSignedOn
        if mandateReceiverName is not None:
            data['mandateReceiverName'] = mandateReceiverName
        if mandateSequence is not None:
            data['mandateSequence'] = mandateSequence
        if informationText is not None:
            data['informationText'] = informationText
        if kassenzeichen is not None:
            data['kassenzeichen'] = kassenzeichen
        if qrcodeReturn is not None:
            data['qrcodeReturn'] = qrcodeReturn
        if billingAddress is not None:
            data['billingAddress'] = billingAddress
        if shippingAddress is not None:
            data['shippingAddress'] = shippingAddress
        if customerInfo is not None:
            data['customerInfo'] = customerInfo
        if basket is not None:
            data['basket'] = basket

        response = self.call_api(url=GIROSOLUTION_PAYPAGE_INIT_URL, data=data)

        response_hash = response.headers.get('hash')
        response_dict = response.json()
        response_text = response.text

        generated_hash = self._generate_hash_from_text(response_text)
        assert response_hash == generated_hash, _(
            "Response hash {} not compatible with the generated hash {}.").format(response_hash, generated_hash)

        if response_dict.get('reference'):
            from django_girosolution.models import GirosolutionTransaction
            g_tx = GirosolutionTransaction()
            g_tx.redirect_url = ''
            g_tx.notify_url = notify_url
            g_tx.success_url = success_url
            g_tx.error_url = error_url
            g_tx.project_id = self.payment.get('PROJECT_ID')
            g_tx.merchant_id = self.payment.get('MERCHANT_ID')
            g_tx.merchant_tx_id = merchant_tx_id
            g_tx.amount = amount
            g_tx.currency = currency
            g_tx.latest_response_code = response_dict.get('rc')
            g_tx.purpose = purpose[:27]
            g_tx.reference = response_dict.get('reference')
            g_tx.payment_type = 'PAYPAGE'
            g_tx.paypage_url = response_dict.get('url')
            g_tx.save()
        else:
            logger.error(_("no reference given by response"))
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
            if hasattr(e, 'errno'):
                logger.error("Girosolution Error {0}({1})".format(e.errno, e.strerror))
            else:
                logger.error(
                    "Girosolution Error({0})".format(e.strerror))
        else:
            try:
                response_dict = response.json()
                rc = response_dict.get('rc')
                if rc is not None and str(rc).startswith('5'):
                    logger.error(f'Girosolution API error rc={rc}: {response_dict.get("msg")}')
            except ValueError as ex:
                logger.error(f'Girosolution API ValueError: {ex}')
            if not response.ok:
                logger.error(f'Girosolution API error {response.code}: {response.text}')
            return response
        return False
