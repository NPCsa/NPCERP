{
    'name': 'OdooTec Entry Print',
    'version': '11.0',
    'category': 'Accounting',
        'sequence': 1,
    'summary': "Print of Account Entry",
    'description':"Print of Account Entry",
    'author': 'OdooTec',
    'depends': ['account','web'],
    'data': [
        'views/entry_report.xml',
        'entry_print_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}


