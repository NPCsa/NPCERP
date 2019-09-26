# -*- coding: utf-8 -*-
{
    'name': "Payrolls Employee Report",

    'summary': """
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "OdooTec",
    'website': "http://www.odootec.com",

    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll','odt_zawaj_hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/report.xml',
        'wizard/payroll_analysis_view.xml',
        'views/hr_payslip_report.xml',
    ],
}