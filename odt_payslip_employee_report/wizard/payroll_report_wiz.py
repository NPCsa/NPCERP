# -*- coding:utf-8 -*-

import time
from odoo import models, fields, api, _
from datetime import datetime
from dateutil import relativedelta


class PayrollEmployee(models.TransientModel):
    _name = 'payroll.employee.wiz'

    date_from = fields.Date(string="Date From", required=True, default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string="Date To", required=True,
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    department_ids = fields.Many2many('hr.department', string='Department')
    location_ids = fields.Many2many('hr.idara', string='Location')
    employee_ids = fields.Many2many('hr.employee', string='Employees')

    # @api.onchange('department_ids')
    # def onchange_department_ids(self):
    #     data = [emp.id for department in self.department_ids for emp in
    #             self.env['hr.employee'].search([('department_id', '=', department.id)])]
    #     if self.employee_ids:
    #         data += self.employee_ids.ids
    #         data = list(set(data))
    #     self.employee_ids = data
    #
    # @api.onchange('location_ids')
    # def onchange_location_ids(self):
    #     data = [emp.id for location in self.location_ids for emp in
    #             self.env['hr.employee'].search([('zw_idara', '=', location.id)])]
    #     if self.employee_ids:
    #         data += self.employee_ids.ids
    #         data = list(set(data))
    #     self.employee_ids = data

    @api.multi
    def print_report(self):
        data = {'ids': self.ids, 'model': self._name, 'form': self.read()[0]}
        return self.env.ref('odt_payslip_employee_report.action_hr_payroll_employee').report_action(self, data=data, config=False)

