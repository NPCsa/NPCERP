# -*- coding: utf-8 -*-
{
    'name': "Collection by in account payment and print",
    'summary': """ Collection by in account payment and print""",
    'description': """
        Collection by in account payment and print.
 """,
    'author': "OdooTec",
    'website': "www.odootec.com",
    'category': 'account',
    'version': '1.0.1',
    'depends': ['account'],
    'data': [
        "security/security_view.xml",
        "views/payment_view.xml",
    ],
    'installable': True,
}
