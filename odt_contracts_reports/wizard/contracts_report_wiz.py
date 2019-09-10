# -*- coding:utf-8 -*-

import time
from odoo import models, fields, api, _
from datetime import datetime
from dateutil import relativedelta


class contractsEmployee(models.TransientModel):
    _name = 'contracts.employee.wiz'

    date_from = fields.Date(string="Date From", required=True, default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string="Date To", required=True, )
    department_ids = fields.Many2many('hr.department', string='Department')
    location_ids = fields.Many2many('hr.idara', string='Location')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    filter_by = fields.Selection(string="Filter By", selection=[('depart', 'Department'), ('location', 'Location'),
                                                                ('employee', 'Employee'), ], default='employee',
                                                                required=True, )
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('pending', 'To Renew'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
        ('all', 'All')
    ], default='open', string="Status", required=True, )

    @api.onchange('filter_by')
    def _onchange_filter_by(self):
        self.department_ids = False
        self.location_ids = False
        self.employee_ids = False

    @api.multi
    def print_report(self):
        data = {'ids': self.ids, 'model': self._name, 'form': self.read()[0]}
        return self.env.ref('odt_contracts_reports.action_hr_contracts_employee').report_action(self, data=data,
                                                                                                    config=False)
