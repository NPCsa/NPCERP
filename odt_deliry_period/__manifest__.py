# -*- coding: utf-8 -*-
{
    'name': "odt_deliry_period",
    'description': """
        Add deliery Period in sales
    """,
    'author': "Odootec",
    'website': "http://www.odootec.com",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}