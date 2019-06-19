# -*- coding: utf-8 -*-\

from odoo import api, fields, models

class HrClearance(models.Model):
    _inherit = 'hr.clearance'

    custody_ids = fields.One2many('hr.custody.line', 'custody_id', 'Employee Custody',)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        employee = self.env['hr.custody'].search([('employee_id', '=', self.employee_id.id)])
        if employee:
            self.custody_ids = employee.ohda_line.filtered(lambda type : type.state_3ohda == 'deliver').ids
