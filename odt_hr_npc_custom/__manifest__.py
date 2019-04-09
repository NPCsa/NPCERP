# -*- coding: utf-8 -*-
{
    'name': "OdooTec Hr NPCsa Customization",
    'description': """
        1. Includes Modification in contract and Payslip
 """,
    'author': "OdooTec",
    'website': "www.odootec.com",
    'category': 'Hr',
    'version': '1.0.1',
    'depends': ['hr_payroll'],
    'data': [

        'views/hr_payroll_view.xml',
        'views/payslip_report_custom.xml',
    ],
    'installable': True,
    'auto_install': False,

}
