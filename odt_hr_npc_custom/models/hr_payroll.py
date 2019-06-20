# -*- coding: utf-8 -*-

from __future__ import division
from dateutil import relativedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    struct_id = fields.Many2one('hr.payroll.structure', string='Structure', related='contract_id.struct_id',
                                readonly=True, states={'draft': [('readonly', False)]},
                                help='Defines the rules that have to be applied to this payslip, accordingly '
                                     'to the contract chosen. If you let empty the field contract, this field isn\'t '
                                     'mandatory anymore and thus the rules applied will be all the rules set on the '
                                     'structure of all contracts of the employee valid for the chosen period')


    @api.model
    def create(self, values):
        res = super(Payslip, self).create(values)
        if not res.employee_id.active:
            raise UserError(_('You Cannot Create Payslip For Archive Employee.%s')%(res.employee_id.name))
        if not res.contract_id:
            raise UserError(_('You Cannot Create Payslip For Employee %s has not contract.')%(res.employee_id.name))
        return res

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        res = super(Payslip, self).get_worked_day_lines(contract_ids, date_from, date_to)
        working_days = 0.0
        hours_per_day = 8.0
        for contract in contract_ids:
            hours_per_day = contract.resource_calendar_id.hours_per_day or 8.0
            if str(contract.date_start) > str(date_from):
                date_from = fields.Datetime.from_string(date_from)
                start_date = fields.Datetime.from_string(contract.date_start)
                diff = start_date - date_from
                working_days += diff.days
            if str(contract.date_end) < str(date_to):
                date_to = fields.Datetime.from_string(date_to)
                end_date = fields.Datetime.from_string(contract.date_end)
                diff = date_to - end_date
                working_days += diff.days
        for rule in res:
            if rule['code'] == 'WORK100':
                rule['number_of_days'] = float(rule['number_of_days']) - working_days
                rule['number_of_hours'] = float(rule['number_of_hours']) - (working_days * hours_per_day)
        return res

class PayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    state = fields.Selection(selection_add=[('done', 'Confirm')])

    @api.onchange('date_start', 'date_end')
    def onchange_batch_dates(self):
        if self.date_start:
            date_from = fields.Datetime.from_string(self.date_start)
            self.date_end = str(date_from + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10]

    @api.multi
    def compute_sheet(self):
        if self.slip_ids:
            for line in self.slip_ids:
                line.compute_sheet()

    @api.multi
    def action_payslip_done(self):
        if self.slip_ids:
            for line in self.slip_ids.filtered(lambda pay: pay.state == 'draft'):
                line.action_payslip_done()
        self.write({'state': 'done'})