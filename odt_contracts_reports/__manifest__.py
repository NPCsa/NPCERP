# -*- coding: utf-8 -*-
{
    'name': "Contracts Employee Report",

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
    'depends': ['base','hr','hr_payroll','odt_zawaj_hr','odt_hr_shada'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/report.xml',
        'wizard/contracts_analysis_view.xml',
        'views/hr_contracts_report.xml',
    ],
}