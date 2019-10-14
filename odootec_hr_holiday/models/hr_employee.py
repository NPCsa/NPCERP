# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.float_utils import float_round


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
    remaining_allocate_leaves = fields.Float(
        compute='_compute_allocate_leaves', string='Remaining Annual Leaves',
        help='Total number of legal leaves allocated to this employee, change this value to create allocation/leave request. '
             'Total based on all the leave types on allocation Leaves.')

    @api.multi
    def _compute_allocate_leaves(self):
        for employee in self:
            leaves = employee.holiday_line_ids.mapped('leave_status_id').ids
            leave_request = self.env['hr.leave'].search(
                [('employee_id', '=', employee.id), ('state', '=', 'validate'), ('holiday_status_id', 'in', leaves)])
            leave_allocate = self.env['hr.leave.allocation'].search(
                [('employee_id', '=', employee.id), ('state', '=', 'validate'), ('holiday_status_id', 'in', leaves)])
            allocate_days = sum(leave_allocate.mapped('number_of_days'))
            request_days = sum(leave_request.mapped('number_of_days'))
            days = allocate_days - request_days
            employee.remaining_allocate_leaves = days if days > 0.0 else 0.0

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
