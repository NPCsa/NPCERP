# -*- coding: utf-8 -*-
{
    'name': "odt_leave_location",

    'summary': """
        Report for Leaves with filter Department and Location""",


    'author': "Odootec",
    'website': "http://www.odootec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Report',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','odt_zawaj_hr','timesheet_grid','hr_holidays'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/employee_detail_wiz_view.xml',
        'views/views.xml',
        'views/templates.xml',
    ]
}