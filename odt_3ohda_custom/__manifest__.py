# -*- coding: utf-8 -*-
{
    'name': "Employee 3ohda",

    'summary': """
        Employee 3ohda Of Asset Or Expense""",

    'description': """
        Long description of module's purpose
    """,

    'author': "OdooTec",
    'website': "http://www.odootec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','account','account_asset','odt_hr_custom'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/employee_3ohda_view.xml',
        'views/account_invoice_view.xml',
        'views/account_asset_view.xml',
        'views/hr_clearance_view.xml',
        'views/report_3ohda_veiw.xml',
    ],
}