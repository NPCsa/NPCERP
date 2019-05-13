{
    'name': 'OdooTec Entry Print',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 1,
    'summary': "Print of Account Entry",
    'description': "Print of Account Entry",
    'author': 'OdooTec',
    'depends': ['account'],
    'data': [
        # 'security/security.xml',
        'views/entry_report.xml',
        # 'views/account_move_view.xml',
        'entry_print_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
