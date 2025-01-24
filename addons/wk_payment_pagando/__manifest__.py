# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

{
    "name": "Website Pagando Payment Gateway",
    "summary": """Website Pagando Payment Gateway""",
    "category": "Website",
    "version": "1.0.0",
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "license": "Other proprietary",
    "website": "https://store.webkul.com/",
    "description": """Website Pagando Payment Gateway""",
    "depends": ["payment"],
    "data": [
        "views/payment_provider_views.xml",
        "views/payment_pagando_template.xml",
        "data/pagando_payment_data.xml",
    ],
    "images": [],
    "installable": True,
    "auto_install": False,
    "pre_init_hook": "pre_init_check",
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
