# -*- coding: utf-8 -*-
{
    'name': "Employee Payslip Report",

    'summary': """
       Details Of Payslip Of Employees In Company""",

    'description': """
        Long description of module's purpose
    """,

    'author': "OdooTec",
    'website': "http://www.odootec.com",

    'category': 'payroll',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll', 'hr', 'report_xlsx', 'odt_zawaj_hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/report.xml',
        'wizard/payroll_analysis_view.xml',

    ],
}
