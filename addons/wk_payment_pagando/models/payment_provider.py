# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class PagandoPaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(
        selection_add=[("pagando", "Pagando")], ondelete={"pagando": "set default"}
    )
    pagando_user_id = fields.Char(
        string="Pagando User ID",
        required_if_provider="pagando",
        groups="base.group_system",
    )
    pagando_api_key = fields.Char(
        string="Pagando Api Key",
        required_if_provider="pagando",
        groups="base.group_system",
    )
    pagando_webhook_token = fields.Char(
        string="Pagando Webhook Token",
        required_if_provider="pagando",
        groups="base.group_system",
    )
    pagando_return_url = fields.Char(
        string="Pagando Return Url",
        required_if_provider="pagando",
        compute="_get_pagando_return_url",
        groups="base.group_system",
    )
    pagando_callback_url = fields.Char(
        string="Pagando Callback Url",
        required_if_provider="pagando",
        compute="_get_pagando_callback_url",
        groups="base.group_system",
    )

    def _pagando_base_url(self):
        try:
            website = self.env["website"].sudo().get_current_website()
            base_url = website.get_base_url()
        except:
            base_url = self.get_base_url()
        return base_url

    def _get_pagando_return_url(self):
        url = self._pagando_base_url()
        for rec in self:
            rec.pagando_return_url = "%s/payment/status" % (url)

    def _get_pagando_callback_url(self):
        url = self._pagando_base_url()
        for rec in self:
            rec.pagando_callback_url = "%s/payment/pagando/callback" % (url)
