{
    'name': 'Zawaj Hr Customization',
    'version': '1.0',
    'author': 'Odootec',
    'category': 'accounting',
    'website': '',
    'description': """
    """,
    'depends': ['odt_hr_custom', 'hr_contract', 'hr_payroll_account', 'hr_payroll','odt_hr_shada', 'odt_employee_name'],
    'data': [
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_payslip_view.xml',
        'security/ir.model.access.csv',
        'security/hr_security.xml',
    ],
    'installable': True,
    'auto_install': False,
}
