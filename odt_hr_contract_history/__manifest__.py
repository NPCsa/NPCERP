# -*- coding: utf-8 -*-
{
    'name': "OdooTec Hr Contract History",
    'description': """
        1. Includes some fields in contract
 """,
    'author': "OdooTec",
    'website': "www.odootec.com",
    'category': 'Hr',
    'version': '1.0.1',
    'depends': [
        'base','odt_hr_shada', 'hr', 'hr_contract',git 
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/contract_view.xml',
    ],
}
