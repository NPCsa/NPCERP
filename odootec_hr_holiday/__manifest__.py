# -*- coding: utf-8 -*-
{
    'name': "OdooTec Hr Holiday Customization",

    'summary': """ Leave Management """,

    'description': """
        Automatic process for allocating leaves at the end of every month or year.
        Leave Report
    """,

    'author': "OdooTec",
    'website': "www.odootec.com",


    'category': 'HR',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','hr_holidays','hr_contract'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_holiday_view.xml',
        'views/hr_employee_view.xml',
        'views/report.xml',
        'views/hr_holiday_report.xml',
        'wizard/holiday_analysis_view.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'installable': True,
    'auto_install': False,
    'application': True,
}