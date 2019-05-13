# -*- coding: utf-8 -*-
{
    'name': "odt_edit_npc",

    'summary': """
        Editing Requirements in Account , Sale and Purchase Models""",


    'author': "OdooTec",
    'website': "http://www.odootec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale','sale_management','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/account_move.xml',
        'views/purchase_view.xml',
        # 'views/sale_view.xml',
    ]
}