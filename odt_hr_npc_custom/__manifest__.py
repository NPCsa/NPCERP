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
    'depends': ['base','hr_payroll','account','hr_holidays','odt_effective_date_notice'],
    'data': [

        # 'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_payroll_view.xml',
        'views/payslip_report_custom.xml',
        'views/working_schedule_view.xml',
    ],
    'installable': True,
    'auto_install': False,

}
