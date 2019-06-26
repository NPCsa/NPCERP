from odoo import models, api, fields
from datetime import datetime

class EmployeeContract(models.Model):
    _inherit = 'hr.contract'

    name = fields.Char('Contract Reference', readonly=True,compute="get_ref")
    gossi_reg_no = fields.Char('Gossi Registration Number')
    total_salary = fields.Monetary('Total Salary', digits=(16, 2), compute='_compute_total_salary', track_visibility="onchange", help="Employee's monthly Total Salary.")
    zw_idara = fields.Many2one(related='employee_id.zw_idara', string='Location')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    @api.depends('employee_id')
    def get_ref(self):
        self.name = str(self.employee_id.employee_id) + '/' + str(datetime.now().year)

    @api.one
    def _compute_total_salary(self):
        for record in self:
            record.total_salary = record.wage + record.overtime_allowance + record.work_allowance + record.reward + record.transportation_allowance + record.housing_allowance + record.mobile_allowance + record.other_allowance
