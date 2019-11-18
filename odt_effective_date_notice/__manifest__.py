# -*- coding: utf-8 -*-
{
    'name': "Effective Date Notice",

    'summary': """
        Effective Date Notice  """,
    'description': """
        Effective Date Notice""",

    'author': "OdooTec",
    'website': "http://www.odootec.com",
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','hr_holidays'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/date_notice.xml',
        'views/hr_view.xml',
    ]
}
