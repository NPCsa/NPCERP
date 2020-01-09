# -*- coding: utf-8 -*-
{
    'name': "Payment Term in sale and invoice",
    'summary': """ Payment Term in sale and invoice""",
    'description': """
        Payment Term in sale and invoice.
 """,
    'author': "OdooTec",
    'website': "www.odootec.com",
    'category': 'sale',
    'version': '1.0.1',
    'depends': ['sale','account'],
    'data': [
        "views/payment_term.xml",
        

    ],
    'installable': True,
}
