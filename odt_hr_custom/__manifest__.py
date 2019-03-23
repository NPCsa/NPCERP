# -*- coding: utf-8 -*-
{
    'name': "OdooTec Hr Customization",
    'summary': """HR Custom + Add Clearance feature to HR module""",
    'description': """
    included


     1. Employee type
     2. Employee Code (employee code depends employee type)
     3. Employee Status
     4. Identification Details( Iqama, passport etc)
     5. Family Details
     6. Educational status
     7. Clearance Form
     8. Notification for expired passport and iqama

     New Modifications

     1.change field display_name into name from the kanban and tree view of partner.

 """,
    'author': "OdooTec",
    'website': "www.odootec.com",
    'category': 'HR',
    'version': '1.0.1.1',
    'depends': [
        'mail', 'hr_contract','odt_employee_name',
    ],
    'data': [
        'data/clearance_data.xml',
        'views/hr_clearance_view.xml',
        'views/hr_clearance_report.xml',
        'views/hr_view.xml',
        'views/res_partner_view.xml',
        'views/hr_notification_view.xml',
        'security/ir.model.access.csv',
        'views/report.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
