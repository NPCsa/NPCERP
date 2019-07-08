# -*- coding: utf-8 -*-

{
    'name': 'Create RFQ from Purchase Request',
    'version': '1.0',
    'summary': 'Create RFQ from Purchase Request',
    'author': 'Srikesh Infotech',
    'license': "AGPL-3",
    'website': 'http://www.srikeshinfotech.com',
    'description': """
        This module helps to create RFQ
        from the purchase request lines.
    """,
    'price': 10,
    'currency': 'EUR',
    'images': ['images/main_screenshot.png'],
    'category': "Purchase Management",
    'depends': ['skit_po_request'],

    "data": [
        "views/create_po_view.xml",
        "security/ir.model.access.csv",
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
