# -*- coding: utf-8 -*-
{
    'name': "OdooTec Hr Shada Customization",
    'description': """
        1. Includes some fields in contract
 """,
    'author': "OdooTec",
    'website': "www.odootec.com",
    'category': 'Hr',
    'version': '1.0.1',
    'depends': [
        'hr_payroll','hr_expense'
    ],
    'data': [
        'views/hr_view.xml',
        'views/partner_view.xml'
        ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
