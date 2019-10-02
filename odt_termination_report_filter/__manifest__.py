# -*- coding: utf-8 -*-
{
    'name': "odt_termination_report_filter",

    'summary': """
        Report for Termination and Termination Leaves with filter Department and Location""",


    'author': "OdooTec",
    'website': "http://www.odootec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Termination',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','odt_end_of_service','odt_zawaj_hr','odootec_hr_holiday','odt_leave_termination'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/view.xml',
        'views/termination_report_wizard.xml',
        'views/holiday_detail_wiz_view.xml',
        'wizard/employee_detail_wiz_view.xml',
        'wizard/holiday_detail_wiz_view.xml',
    ]
}