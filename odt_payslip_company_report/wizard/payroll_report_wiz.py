# -*- coding:utf-8 -*-

import time
from odoo import models, fields, api, _
from datetime import datetime
from dateutil import relativedelta


class PayrollCompany(models.TransientModel):
    _name = 'payroll.company.wiz'

    date_from = fields.Date(string="Date From", required=True, default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string="Date To", required=True,
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    department_ids = fields.Many2many('hr.department', string='Department')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    rule_ids = fields.Many2many('hr.salary.rule', string='Salary Rules')
    state = fields.Selection(string="Status", selection=[('all', 'All Payslip'), ('draft', 'Draft'),('done', 'Done'), ], required=False, )

    @api.onchange('department_ids')
    def onchange_department_ids(self):
        data = [emp.id for department in self.department_ids for emp in
                self.env['hr.employee'].search([('department_id', '=', department.id)])]
        if self.employee_ids:
            data += self.employee_ids.ids
            data = list(set(data))
        self.employee_ids = data

    @api.multi
    def print_report(self):
        return self.env.ref('odt_payslip_company_report.report_payroll_company_xlsx').report_action(self)
