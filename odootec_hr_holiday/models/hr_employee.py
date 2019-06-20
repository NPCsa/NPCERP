# -*- coding: utf-8 -*-
from odoo import models, fields


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    eligible = fields.Boolean(string='Eligible for Leave?', readonly=False)
    calculate_type = fields.Selection(string="Calculation Type",
                                      selection=[('manual', 'Manual'), ('automatic', 'Automatically'), ],
                                      required=False, )
    holiday_line_ids = fields.One2many('hr.employee.leave.line', 'employee_id', 'Holiday Lines')
    holiday_line_man_ids = fields.One2many('hr.employee.leave.line.manual', 'employee_id', 'Holiday Lines')
    joining_date = fields.Date('Joining Date', required=False)
    last_allocation_date = fields.Date(string="Last Allocation Date", required=False, )
    last_return_date = fields.Date(string="Last Return Date", required=False, )
    allocation_method = fields.Many2one('hr.leave.allocation.method', 'Allocation Method',
                                        help='Allocation method for Settlement')


class HrEmployeeLeaveLineAuto(models.Model):
    _name = 'hr.employee.leave.line'

    leave_status_id = fields.Many2one('hr.leave.type', 'Leave Type', required=True)
    allocation_range = fields.Selection([('month', 'Month'), ('year', 'Year')],
                                        'Allocate automatic leaves every', required=True,
                                        help="Periodicity on which you want automatic allocation of leaves to eligible employees.")
    days_to_allocate = fields.Float('Days to Allocate',
                                    help="In automatic allocation of leaves, " \
                                         "given days will be allocated every month / year.")
    employee_id = fields.Many2one('hr.employee', ondelete='cascade')

class HrEmployeeLeaveLineMan(models.Model):
    _name = 'hr.employee.leave.line.manual'

    name = fields.Char(string="Description", required=False, )
    leave_status_id = fields.Many2one('hr.leave.type', 'Leave Type', required=True)
    employee_id = fields.Many2one('hr.employee', ondelete='cascade')
