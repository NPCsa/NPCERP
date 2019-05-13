{
    'name': 'OdooTec Entry Print',
    'version': '1.0',
    'category': 'Accounting',
        'sequence': 1,
    'summary': "Print of Account Entry",
    'description':"Print of Account Entry",
    'author': 'OdooTec',
    'depends': ['account'],
    'data': [
        'views/entry_report.xml',
        'entry_print_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}


