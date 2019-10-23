# -*- coding: utf-8 -*-
{
    'name': "Compute Leave Balance",

    'summary': """""",

    'description': """
        Long description of module's purpose
    """,

    'author': "OdooTec",
    'website': "http://www.odootec.com",


    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','odt_hr_custom','hr_holidays','odt_hr_shada','odootec_hr_holiday'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_termination_sequence.xml',
        'views/termination_view.xml',
        'views/report.xml',
    ],

}