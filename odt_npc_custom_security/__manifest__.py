# -*- coding: utf-8 -*-
{
    'name': "NPC Security Custom",
    'summary': """ NPC Security Custom""",
    'description': """
        NPC Security Custom
 """,
    'author': "OdooTec",
    'website': "www.odootec.com",
    'category': 'access',
    'version': '1.0.1',
    'depends': ['purchase','sale','account','hr_payroll','hr_expense','account'],
    'data': [
        "security/security_view.xml",
        "views/button_access_view.xml",
        

    ],
    'installable': True,
}
