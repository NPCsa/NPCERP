# -*- coding: utf-8 -*-
{
    'name': "OdooTec Leave Customization",
    'summary': """ HR Management""",
    'description': """
    Control in Leaves on Payroll.
 """,
    'author': "OdooTec",
    'website': "www.odootec.com",
    'category': 'Hr',
    'version': '1.0.1',
    'depends': [
        'hr_holidays','hr_payroll'
    ],
    'data': [
        'views/hr_leave_type_view.xml',
        'views/hr_payslip_view.xml'

    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
