# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

import logging
import requests
import base64
from werkzeug import urls
from odoo import models, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import html2plaintext
_logger = logging.getLogger(__name__)

class PagandoPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'pagando':
            return res
        return self.pagando_form_generate_values()

    def get_pagando_tx_sale_invoice_rec(self):
        lines,qty = None,None
        if hasattr(self, 'sale_order_ids') and self.sale_order_ids:
            lines = self.sale_order_ids[0].order_line.filtered(lambda x: not x.is_delivery)
            qty = 'product_uom_qty'
        elif hasattr(self, 'invoice_ids') and self.invoice_ids:
            lines = self.invoice_ids[0].invoice_line_ids.filtered(lambda x: x.price_unit > 0)
            qty = 'quantity'
        return lines,qty

    def _get_pagando_payload_data(self):
        lines,qty = self.get_pagando_tx_sale_invoice_rec()
        payload = {}
        files = []
        for count,line in enumerate(lines):
            payload.update({
                    f'products[{count}][title]': line.product_id.name,
                    f'products[{count}][description]': html2plaintext(line.product_id.description) or line.product_id.name,
                    f'products[{count}][price]': line.product_id.taxes_id.compute_all(line.product_id.lst_price).get('total_included') \
                                            if line.product_id.taxes_id else line.product_id.lst_price,
                    f'products[{count}][count]': int(getattr(line,qty)),
                    f'products[{count}][pagandoUserId]': self.provider_id.pagando_user_id,
                })
            files.append((f'products[{count}][image]',('image.png',base64.b64decode(line.product_id.image_1920) if line.product_id.image_1920 else line.product_id.image_1920,'image/png')))
        payload.update({
            'metadata[client][name]' : self.partner_id.name,
            'metadata[client][phone_number]' : self.partner_id.phone,
            'metadata[client][email]' : self.partner_id.email,
            'metadata[total_amount]' : self.amount,
            'metadata[currency]' : self.currency_id.name,
            'metadata[order_reference]' : self.reference,
            'metadata[return_url]' : self.provider_id.pagando_return_url,
            'metadata[callback_url]' : self.provider_id.pagando_callback_url,
        })
        return payload ,files

    def pagando_form_generate_values(self):
        url = f"https://checkout-api.pagando.tech/api/v1/products-odoo/{self.reference.replace("/","-")}?pagando-api-key={self.provider_id.pagando_api_key}"
        headers={}
        payload,files = self._get_pagando_payload_data()
        try:
            result = requests.request("POST",url, headers=headers, data=payload,files=files,verify=False).json()
            _logger.info(f'\n Pagando Checkout Api Response {result} \n')
            if result.get('data',False):
                return {
                    "pagando_checkout_url": result.get('data').get('url',False)
                }
            else:
                raise UserError(result.get('errorCode',False))
        except Exception as e:
            _logger.warning("#WKDEBUG---PAGANDO----Exception-----%r---------" % (e))
            raise UserError(e)

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'pagando' or len(tx) == 1:
            return tx
        reference = notification_data.get('order_reference',False)
        if not reference:
            raise ValidationError("Pagando Payment: " + _("Received data with missing reference."))

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'pagando')])
        if not tx:
            raise ValidationError(
                "Pagando Payment: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, notification_data):
        self.ensure_one()
        super()._process_notification_data(notification_data)
        if self.provider_code != 'pagando':
            return 
        self.write({'provider_reference': notification_data.get('transaction_id',False)})
        if notification_data.get('payment_status') == 'Paid':
            self._set_done()
        elif notification_data.get('payment_status') == 'Cancelled':
            self._set_canceled()
        elif notification_data.get('payment_status') == 'Pending':
            self._set_pending()
        elif notification_data.get('payment_status') == 'Failed':
            error_msg = notification_data.get('payment_msg',False)
            self._set_error(error_msg)

