# -*- coding: utf-8 -*-
{
    'name': "Payslips Bank Report",

    'summary': """
        Raise Salaries of Employee To Bank""",

    'description': """
        Raise Salaries of Employee To Bank
    """,

    'author': "OdooTec",
    'website': "http://www.odootec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx','hr_payroll','odt_zawaj_hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/payroll_analysis_view.xml',
        'report/report.xml',

    ],
}