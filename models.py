from __future__ import unicode_literals

import logging

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class GirosolutionTransaction(models.Model):
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    reference = models.TextField(_("reference"), null=True)
    backend_tx_id = models.TextField(_("backend tx id"), null=True)
    merchant_tx_id = models.CharField(_("merchant tx id"), max_length=255, unique=True)

    merchant_id = models.IntegerField(_("amount in Cents"))
    project_id = models.IntegerField(_("amount in Cents"))

    amount = models.PositiveIntegerField(_("amount in Cents"))
    currency = models.CharField(_("Currency Code (3 Chars)"), max_length=3, default='EUR')
    purpose = models.CharField(_("purpose"), max_length=27)

    redirect_url = models.TextField(_("redirect url"))
    notify_url = models.TextField(_("notify url"))
    success_url = models.TextField(_("success url"))
    error_url = models.TextField(_("error url"))

    payment_type = models.CharField(_("paymentname"), max_length=128)

    result_payment = models.IntegerField(_("return code from girosolution transaction"), null=True)

    result_avs = models.IntegerField(_("return code of girosolution age verification"), null=True, blank=True)
    obv_name = models.TextField(_("obv name"), null=True, blank=True)

    latest_response_code = models.IntegerField(_("rc field from girosolution response"),
                                               null=True)
    latest_response_msg = models.TextField(_("msg field from girosolution response"), blank=True,
                                           null=True)

    objects = models.Manager()

    def __str__(self):
        return self.merchant_tx_id

    class Meta:
        verbose_name = _("Girosolution Transaction")
        verbose_name_plural = _("Girosolution Transaction")
