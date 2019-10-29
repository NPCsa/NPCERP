# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrContractReport(models.Model):
    _name = 'hr.contract.history'
    _rec_name = 'contract_id'
    _description = "Contract History"
    _inherit = ['mail.thread']

    date = fields.Date(string="Date", required=True, )
    user_id = fields.Many2one(comodel_name="res.users", string="Edited By", readonly=True,
                              default=lambda self: self.env.user)
    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('done', 'Done'), ],default='draft', )
    contract_id = fields.Many2one(comodel_name="hr.contract", string="Contract", required=True, )
    wage = fields.Float('Basic Salary', digits=(16, 2), )
    transportation_allowance = fields.Float('Transportation', )
    housing_allowance = fields.Float('Housing', )
    mobile_allowance = fields.Float('Mobile', )
    overtime_allowance = fields.Float('OverTime', )
    work_allowance = fields.Float('Work', )
    reward = fields.Float('Reward', )
    other_allowance = fields.Float('Other', )
    deduction = fields.Float('Deduction', )

    @api.multi
    def assign_contract_values(self):
        for record in self:
            vals = {
                'wage': record.wage,
                'transportation_allowance': record.transportation_allowance,
                'housing_allowance': record.housing_allowance,
                'mobile_allowance': record.mobile_allowance,
                'overtime_allowance': record.overtime_allowance,
                'work_allowance': record.work_allowance,
                'reward': record.reward,
                'other_allowance': record.other_allowance,
                'deduction': record.deduction,
            }
            record.contract_id.write(vals)
            record.state = 'done'
