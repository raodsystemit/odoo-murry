# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

import logging
import pprint
from werkzeug.exceptions import Forbidden
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.tools import consteq

_logger = logging.getLogger(__name__)


class PagandoController(http.Controller):

    @http.route(
        "/payment/pagando/callback",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def pagando_payment_callback(self, **kwargs):
        data = request.get_json_data()
        _logger.info(
            f"########### Callback received from Pagando with data :{pprint.pformat(data)}"
        )
        try:
            received_token = request.httprequest.headers.get(
                "pagando-webhook-token", ""
            )
            tx_sudo = (
                request.env["payment.transaction"]
                .sudo()
                ._get_tx_from_notification_data("pagando", data)
            )
            self._verify_notification_token(received_token, tx_sudo)
            _logger.info(f"########### token verified #########")
            tx_sudo._handle_notification_data("pagando", data)
            _logger.info(f"########### handled callback data successfully #########")
        except ValidationError:
            _logger.exception(
                "Unable to handle callback data; skipping to acknowledge."
            )

        return request.make_json_response(["success"], status=200)

    def _verify_notification_token(self, received_token, tx_sudo):
        if not received_token:
            _logger.warning("Received callback with missing token.")
            raise Forbidden()

        if not consteq(tx_sudo.provider_id.pagando_webhook_token, received_token):
            _logger.warning(
                "Received callback with invalid callback token %r.", received_token
            )
            raise Forbidden()
