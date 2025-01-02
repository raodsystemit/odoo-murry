# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

from . import controllers
from . import models

from odoo.addons.payment import setup_provider, reset_payment_provider

def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import UserError
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != '18.0':
        raise UserError('Module support Odoo series 18.0 found {}.'.format(server_serie))

def post_init_hook(env):
    setup_provider(env, 'pagando')

def uninstall_hook(env):
    reset_payment_provider(env, 'pagando')
