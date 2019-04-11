# -*- coding:utf-8 -*-

from odoo import models, fields, api, _


class PayrollBank(models.TransientModel):
    _name = 'payroll.bank.wiz'

    state = fields.Selection(string="Status", selection=[('draft', 'Draft'), ('done', 'Done'), ], required=True, )
    batch_id = fields.Many2many('hr.payslip.run', string='Batch')
    payslip_id = fields.Many2many('hr.payslip', string='Payslip', domain=[('is_refund', '=', False)])

    @api.onchange('state')
    def onchange_state(self):
        return {'domain': {'batch_id': [('state', 'in', [self.state, 'close'])],
                           'payslip_id': [('state', 'in', [self.state]), ('is_refund', '=', False)]}}

    @api.multi
    def print_report(self):
        return self.env.ref('odootec_payslip_bank_report.report_payroll_bank_xlsx').report_action(self)
