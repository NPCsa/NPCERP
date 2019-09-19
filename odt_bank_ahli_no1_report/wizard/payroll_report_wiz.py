# -*- coding:utf-8 -*-

from odoo import models, fields, api, _


class PayrollBankAhliN1(models.TransientModel):
    _name = 'bank.ahli.n1.wiz'

    state = fields.Selection(string="Status", selection=[('draft', 'Draft'), ('done', 'Done'), ], required=True, )
    batch_id = fields.Many2many('hr.payslip.run', string='Batch')
    payslip_id = fields.Many2many('hr.payslip', string='Payslip', domain=[('is_refund', '=', False)])

    @api.onchange('state')
    def onchange_state(self):
        return {'domain': {'batch_id': [('state', 'in', [self.state, 'close'])],
                           'payslip_id': [('state', 'in', [self.state]), ('is_refund', '=', False)]}}

    @api.multi
    def print_report(self):
        return self.env.ref('odt_bank_ahli_no1_report.report_bank_ahli_n1_xlsx').report_action(self)
