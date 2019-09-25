# -*- coding:utf-8 -*-

import time
from odoo import models, fields, api, _
from datetime import datetime
from dateutil import relativedelta


class PayrollEmployee(models.TransientModel):
    _name = 'contract.employee.wiz'

    date_from = fields.Date(string="Date From", required=True, default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string="Date To", required=True,
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    department_ids = fields.Many2many('hr.department', string='Department')
    location_ids = fields.Many2many('hr.idara', string='Location')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('pending', 'To Renew'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
        ('all', 'All')
    ],default='open',string="Status", required=True,)



    @api.multi
    def print_report(self):
        data = {'ids': self.ids, 'model': self._name, 'form': self.read()[0]}
        return self.env.ref('odt_contract_employee_report.action_hr_contract_employee').report_action(self, data=data, config=False)

