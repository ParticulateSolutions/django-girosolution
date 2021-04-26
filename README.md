Django GiroSolution
============================

Implementation of [GiroCheckout API](https://api.girocheckout.de).
The following doc explain how to set up the GiroCheckout API for django.

## How to install django-giropay?

There are just two steps needed to install django-giropay:

1. Install django-girosolution to your virtual env:

	```bash
	pip install django-girosolution
	```

2. Configure your django installation with the following lines:

	```python
    # django-girosolution
    INSTALLED_APPS += ('django_girosolution', )

    GIROPAY = True
    GIROPAY_ROOT_URL = 'http://example.com'

    # Those are dummy test data - change to your data
    GIROPAY_MERCHANT_ID = "from-payment-provider"
    GIROPAY_PROJECT_ID = "from-payment-provider"
    GIROPAY_PROJECT_PASSWORD = b"from-payment-provider"
	```

    There is a list of other settings you could set down below.

3. Include the notification View in your URLs:

	```python
    # urls.py
    from django.conf.urls import include, url

    urlpatterns = [
        url('^girocheckout/', include('django_girosolution.urls')),
    ]
	```

## What do you need for django-giropay?

1. An merchant account for GiroCheckout
2. Django >= 2.2

## Usage

### Minimal Checkout init example:

```python
from django_girosolution.wrappers import GirosolutionWrapper
girosolution_wrapper = GiropayWrapper()

girosolution_transaction = girosolution_wrapper.start_transaction(
    merchant_tx_id='first-test',
    amount=1000,  # 10 Euro 
    purpose='first test'
)
```

## Copyright and license

Copyright 2021 Particulate Solutions GmbH, under [MIT license](https://github.com/ParticulateSolutions/django-giropay/blob/master/LICENSE).