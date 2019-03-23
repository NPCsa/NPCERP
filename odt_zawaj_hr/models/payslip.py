# -*- coding:utf-8 -*-

import time
from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta

import babel

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    age = fields.Float('Age',compute='_compute_age_service')
    service_period = fields.Float('Service Period',compute='_compute_age_service')
    zw_idara = fields.Many2one(related='employee_id.zw_idara', string='IDARA',store=True)

    @api.one
    def _compute_age_service(self):
        if self.employee_id.birthday:
            today = fields.date.today()
            born = datetime.strptime(str(self.employee_id.birthday), '%Y-%m-%d')
            self.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        if self.employee_id.joining_date:
            today = fields.date.today()
            join_date = datetime.strptime(str(self.employee_id.joining_date), '%Y-%m-%d')
            self.service_period = today.year - join_date.year - ((today.month, today.day) < (join_date.month, join_date.day))


    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        res = super(HrPayslip, self).onchange_employee()
        if self.employee_id.birthday:
            today = fields.date.today()
            born = datetime.strptime(str(self.employee_id.birthday), '%Y-%m-%d')
            join_date = datetime.strptime(str(self.employee_id.joining_date), '%Y-%m-%d')
            self.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            self.service_period = today.year - join_date.year - ((today.month, today.day) < (join_date.month, join_date.day))
        if self.date_from:
            date_from = fields.Datetime.from_string(self.date_from)
            self.date_to = str(date_from + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10]
        return res


    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        res = super(HrPayslip, self).get_worked_day_lines(contract_ids, date_from, date_to)
        for contract in contract_ids:
            overtime = {
                'name': 'Number of Hours Overtime',
                'sequence': 11,
                'code': 'Overtime',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            absence = {
                'name': 'Number of Days Absence',
                'sequence': 12,
                'code': 'Absence',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            unpaid = {
                'name': 'Number of Days UnPaid',
                'sequence': 13,
                'code': 'UnPaid',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            late = {
                'name': 'Number of Hours Late',
                'sequence': 14,
                'code': 'Late',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            res.append(overtime)
            res.append(absence)
            res.append(unpaid)
            res.append(late)
        return res
