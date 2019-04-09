from odoo import models, api, fields,_
from odoo.exceptions import UserError, ValidationError

class EmployeeContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def create(self, values):
        res = super(EmployeeContract, self).create(values)
        if not res.employee_id.active:
            raise UserError(_('You Cannot Create Payslip For Archive Employee.'))
        return res