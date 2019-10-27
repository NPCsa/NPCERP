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
    work = fields.Float('Working Period',compute='_compute_age_service')
    zw_idara = fields.Many2one(related='employee_id.zw_idara', string='Location',store=True)
    is_refund = fields.Boolean(string="Refund")
    employee_code = fields.Char('Employee ID', related='employee_id.employee_id',store=True)
    gosi_in_payslip = fields.Char('Gosi Not Appear In PaySlip',related='employee_id.gosi_in_payslip',store=True)

    @api.multi
    def refund_sheet(self):
        for payslip in self:
            if payslip.is_refund:
                raise UserError(_('You Cannot Refund Payslip More one time.'))
            copied_payslip = payslip.copy(
                {'credit_note': True, 'is_refund': True, 'name': _('Refund: ') + payslip.name})
            payslip.update({'is_refund': True})
            copied_payslip.input_line_ids = payslip.input_line_ids
            copied_payslip.compute_sheet()
            copied_payslip.action_payslip_done()
        formview_ref = self.env.ref('hr_payroll.view_hr_payslip_form', False)
        treeview_ref = self.env.ref('hr_payroll.view_hr_payslip_tree', False)
        return {
            'name': ("Refund Payslip"),
            'view_mode': 'tree, form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % copied_payslip.ids,
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'),
                      (formview_ref and formview_ref.id or False, 'form')],
            'context': {}
        }

    @api.model
    def create(self, values):
        res = super(HrPayslip, self).create(values)
        payrolls = self.search([('employee_id', '=', res.employee_id.id)]).filtered(lambda pay: not pay.is_refund)
        for payroll in payrolls:
            if payroll.id != res.id and not res.is_refund:
                if (payroll.date_to >= res.date_from >= payroll.date_from) or (
                        payroll.date_to >= res.date_to >= payroll.date_from):
                    raise UserError(_('You Cannot Create Two Payslips for one Employee In Same Period.'))
        return res

    @api.one
    def _compute_age_service(self):
        if self.employee_id.birthday:
            today = fields.date.today()
            born = datetime.strptime(str(self.employee_id.birthday), '%Y-%m-%d')
            self.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        if self.employee_id.joining_date:
            today = fields.date.today()
            join_date = datetime.strptime(str(self.employee_id.joining_date), '%Y-%m-%d')
            diff = today - join_date.date()
            self.service_period = round((diff.days / 365) * 12, 2)
        if self.date_from and self.date_to:
            from_date = fields.Datetime.from_string(self.date_from)
            to_date = fields.Datetime.from_string(self.date_to)
            self.work = (to_date - from_date).days + 1


    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        self.contract_id = False
        res = super(HrPayslip, self).onchange_employee()
        if self.employee_id.birthday:
            today = fields.date.today()
            born = datetime.strptime(str(self.employee_id.birthday), '%Y-%m-%d')
            self.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        if self.employee_id.joining_date:
            today = fields.date.today()
            join_date = datetime.strptime(str(self.employee_id.joining_date), '%Y-%m-%d')
            diff = today - join_date.date()
            self.service_period = round((diff.days / 365) * 12, 2)
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
