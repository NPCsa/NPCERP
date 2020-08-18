# -*- coding: utf-8 -*-
{
    'name': "Invoice report custom",

    'summary': """
        Editing vate in invoice report ,""",


    'author': "OdooTec",
    'website': "http://www.odootec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','odt_sale_discount_total'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/report_invoice.xml',
        'views/account_invoice_view.xml',
    ]
}