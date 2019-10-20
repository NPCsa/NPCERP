# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning
from datetime import date, datetime, time
from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import float_compare
from odoo.tools.translate import _


class HrHolidays(models.Model):
    _inherit = 'hr.leave'

    reconcile_option = fields.Selection(string="Reconciliation ?", selection=[('yes', 'Yes'), ('no', 'No'), ],
                                        required=False, )
    is_reconciled = fields.Boolean(string="Is Reconciled")
    leave_on_employee = fields.Boolean(string="Leave On Employee", compute='_compute_leave_on_employee')

    @api.one
    @api.depends('employee_id', 'holiday_status_id')
    def _compute_leave_on_employee(self):
        for leave in self:
            leaves = leave.employee_id.holiday_line_ids.mapped(
                'leave_status_id').ids if leave.employee_id.holiday_line_ids else []
            if leave.holiday_status_id.id in leaves:
                leave.leave_on_employee = True
            else:
                leave.leave_on_employee = False

    @api.multi
    def write(self, values):
        res = super(HrHolidays, self).write(values)
        for record in self:
            payslip_obj = self.env['hr.payslip']
            date_from = record.date_from
            date_to = record.date_to
            employee_id = record.employee_id
            contract_id = payslip_obj.get_contract(employee_id, date_from, date_from)
            if contract_id:
                contract = self.env['hr.contract'].browse(contract_id)
                if contract and contract.date_end and str(contract.date_end) < str(date_from)[:10]:
                    raise Warning(_('The Employee Out Of Work'))
                payslips = payslip_obj.search(
                    [('employee_id', '=', employee_id.id), ('is_refund', '=', False), ('date_from', '<=', date_from),
                     ('date_to', '>=', date_from)])
                if payslips:
                    raise Warning(_('The Employee Have Payslip On This Date'))
            # else:
            #     raise Warning(_('No Contract for This Employee or Check the Starting Date in Contract'))
            days = record._get_number_of_days(date_from, date_to, employee_id.id)
            if values.get('number_of_days'):
                if days != record.number_of_days:
                    raise Warning(_('you Cannot Edit Leave Days'))
        return res

    @api.model
    def create(self, values):
        res = super(HrHolidays, self).create(values)
        payslip_obj = self.env['hr.payslip']
        date_from = res.date_from
        date_to = res.date_to
        employee_id = res.employee_id
        contract_id = payslip_obj.get_contract(employee_id, date_from, date_from)
        if contract_id:
            contract = self.env['hr.contract'].browse(contract_id)
            if contract and contract.date_end and str(contract.date_end) < str(date_from)[:10]:
                raise Warning(_('The Employee Out Of Work'))
            payslips = payslip_obj.search(
                [('employee_id', '=', employee_id.id), ('is_refund', '=', False),
                 ('date_from', '<=', date_from),
                 ('date_to', '>=', date_from)])
            if payslips:
                raise Warning(_('The Employee Have Payslip On This Date'))

        # else:
        #     raise Warning(_('No Contract for This Employee or Check the Starting Date in Contract'))
        days = self._get_number_of_days(date_from, date_to, employee_id.id)
        if values.get('number_of_days'):
            if days != res.number_of_days:
                raise Warning(_('you Cannot Edit Leave Days'))
        return res

    def _check_date(self):
        for holiday in self:
            domain = [
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>=', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                return False
        return True

    _constraints = [
        (_check_date, 'You can not have 2 leaves that overlaps on same day!', ['date_from', 'date_to']),
    ]

    @api.multi
    def run_monthly_scheduler(self):
        """ Runs at the end of every month to allocate Leaves to all
        eligible employees.
        """
        vals = {}
        employee_obj = self.env['hr.employee'].search([('eligible', '=', True), ('calculate_type', '=', 'automatic')])
        for emp in employee_obj:
            if emp.eligible and emp.holiday_line_ids:
                for line in emp.holiday_line_ids:
                    if line.allocation_range == 'month':
                        date_from_dt = datetime.now() - relativedelta(months=1) + relativedelta(day=1)
                        date_to_dt = datetime.now() - relativedelta(months=1) + relativedelta(day=31)
                        date_from = fields.Datetime.from_string(date_from_dt)
                        date_to = fields.Datetime.from_string(date_to_dt)
                        allocate_ids = self.search([('date_from', '>=', date_from),
                                                    ('date_to', '<=', date_to),
                                                    ('employee_id', '=', emp.id),
                                                    ('holiday_status_id', '=', line.leave_status_id.id)])

                        if allocate_ids:
                            continue
                        if emp.joining_date:
                            joining_date = datetime.strptime(str(emp.joining_date), '%Y-%m-%d')
                        elif emp.contract_id:
                            joining_date = datetime.strptime(str(emp.contract_id.date_start), '%Y-%m-%d')
                        else:
                            continue
                        if joining_date <= date_to_dt:
                            if date_from_dt < joining_date <= date_to_dt:
                                days_to_allocate = (line.days_to_allocate / 30) * (
                                        date_to_dt.day - joining_date.day + 1)
                            else:
                                days_to_allocate = line.days_to_allocate
                            vals = {
                                'name': 'Monthly Allocation of ' + line.leave_status_id.name + ' Leaves',
                                'number_of_days': days_to_allocate,
                                'date_from': date_from,
                                'date_to': date_to,
                                'employee_id': emp.id,
                                'holiday_status_id': line.leave_status_id.id
                            }

                    if line.allocation_range == 'year':
                        date_from_dt = datetime.now() - relativedelta(years=1) + relativedelta(month=1) \
                                       + relativedelta(day=1)
                        date_to_dt = datetime.now() - relativedelta(years=1) \
                                     + relativedelta(month=12) + relativedelta(day=31)
                        date_from = fields.Datetime.from_string(date_from_dt)
                        date_to = fields.Datetime.from_string(date_to_dt)
                        allocate_ids = self.env['hr.leave.allocation'].search([('date_from', '>=', date_from),
                                                                               ('date_to', '<=', date_to),
                                                                               ('employee_id', '=', emp.id),
                                                                               ('holiday_status_id', '=',
                                                                                line.leave_status_id.id)])
                        if allocate_ids:
                            continue
                        if emp.joining_date:
                            joining_date = datetime.strptime(str(emp.joining_date), '%Y-%m-%d')
                        elif emp.contract_id:
                            joining_date = datetime.strptime(str(emp.contract_id.date_start), '%Y-%m-%d')
                        else:
                            continue
                        if joining_date <= date_to_dt:
                            if date_from_dt < joining_date <= date_to_dt:
                                days_to_allocate = (line.days_to_allocate / 360) * (
                                        date_to_dt.day - joining_date.day + 1)
                            else:
                                days_to_allocate = line.days_to_allocate

                            vals = {
                                'name': 'Yearly Allocation of ' + line.leave_status_id.name + ' Leaves',
                                'number_of_days': days_to_allocate,
                                'date_from': date_from,
                                'date_to': date_to,
                                'employee_id': emp.id,
                                'holiday_status_id': line.leave_status_id.id,
                            }
                    if vals:
                        self.env['hr.leave.allocation'].create(vals).action_approve()

    # @api.multi
    # def get_employee_balance_leave(self):
    #     for holiday in self:
    #         leave_days = 0.0
    #         if holiday.employee_id.joining_date and holiday.employee_id.calculate_type == 'manual':
    #             today = fields.Datetime.from_string(holiday.date_from)
    #             join_date = fields.Datetime.from_string(holiday.employee_id.joining_date)
    #             last_allocation_date = fields.Datetime.from_string(holiday.employee_id.last_allocation_date)
    #             diff = today.date() - join_date.date()
    #             allocation_days = (today.date() - last_allocation_date.date()).days
    #             service_period = round((diff.days / 365) * 12, 2)
    #
    #             allocation_method = holiday.employee_id.allocation_method
    #             day_allocate_lt = 0.0
    #             day_allocate_gt = 0.0
    #             day_allocate_eq = 0.0
    #             if allocation_method:
    #                 if allocation_method.type_state == 'two':
    #                     day_allocate_lt = allocation_method.first_year / (365 - allocation_method.first_year)
    #                     day_allocate_gt = allocation_method.second_year / (365 - allocation_method.second_year)
    #                     if allocation_days:
    #                         if service_period <= 60:
    #                             leave_days = allocation_days * day_allocate_lt
    #                         else:
    #
    #                             allocate_days = (last_allocation_date.date() - join_date.date()).days
    #                             if allocate_days >= 1825:
    #                                 leave_days = allocation_days * day_allocate_gt
    #                             else:
    #                                 day_to = 0
    #                                 for n in range(0, allocation_days + 1):
    #
    #                                     if allocate_days <= 1825:
    #                                         allocate_days += 1
    #                                         day_to += 1
    #                                     else:
    #
    #                                         days_gt = allocation_days - day_to
    #                                         leave_days = (days_gt * day_allocate_gt) + (day_to * day_allocate_lt)
    #                                         break
    #                 if allocation_method.type_state == 'all':
    #                     day_allocate_eq = allocation_method.all_year / (365 - allocation_method.all_year)
    #                     if allocation_days:
    #                         leave_days = allocation_days * day_allocate_eq
    #
    #             if leave_days:
    #                 if holiday.employee_id.eligible and holiday.employee_id.holiday_line_man_ids:
    #
    #                     for line in holiday.employee_id.holiday_line_man_ids:
    #                         vals = {
    #                             'name': 'Allocation of ' + line.leave_status_id.name + ' Leaves',
    #                             'number_of_days': leave_days,
    #                             'employee_id': holiday.employee_id.id,
    #                             'holiday_status_id': line.leave_status_id.id,
    #                         }
    #                         if line.leave_status_id.id == holiday.holiday_status_id.id:
    #
    #                             if vals:
    #                                 holiday_all = self.env['hr.leave.allocation'].create(vals)
    #                                 holiday_all.action_approve()
    #                                 self.write(
    #                                     {'vacation_id': holiday_all.id, 'last_allocation_date': str(last_allocation_date)})
    #                                 self.employee_id.update({'last_allocation_date': str(today)})

    # @api.multi
    # def action_refuse(self):
    #     for holiday in self:
    #         if holiday.vacation_id:
    #             holiday.employee_id.update({'last_allocation_date': holiday.last_allocation_date})
    #             holiday.vacation_id.action_refuse()
    #             holiday.vacation_id.action_draft()
    #             holiday.vacation_id.unlink()
    #     return super(HrHolidays, self).action_refuse()

    # @api.constrains('state', 'number_of_days', 'holiday_status_id')
    # def _check_holidays(self):
    #     for holiday in self:
    #         if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.allocation_type == 'no':
    #             continue
    #         if holiday.state in ['validate', 'validate1']:
    #             leave_days = holiday.holiday_status_id.get_days(holiday.employee_id.id)[holiday.holiday_status_id.id]
    #             if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
    #                     float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
    #                 raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
    #                                         'Please also check the leaves waiting for validation.'))


class LeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    last_allocation_date = fields.Date(string="Allocation Date", required=False,
                                       default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_change = fields.Boolean(string="Make Allocation Change", )

    leave_on_employee = fields.Boolean(string="Leave On Employee", compute='_compute_leave_on_employee')

    @api.one
    @api.depends('employee_id', 'holiday_status_id')
    def _compute_leave_on_employee(self):
        for leave in self:
            leaves = leave.employee_id.holiday_line_ids.mapped(
                'leave_status_id').ids if leave.employee_id.holiday_line_ids else []
            if leave.holiday_status_id.id in leaves:
                leave.leave_on_employee = True
            else:
                leave.leave_on_employee = False

    @api.one
    @api.constrains('date_change', 'last_allocation_date')
    def _check_date_allocation(self):
        date_allocation = fields.Date.from_string(self.last_allocation_date).day
        if not self.date_change and date_allocation != 1 and self.leave_on_employee:
            raise ValidationError("You Must Allocate On First Day Of Month")

    _sql_constraints = [
        ('type_value',
         "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or "
         "(holiday_type='category' AND category_id IS NOT NULL) or "
         "(holiday_type='department' AND department_id IS NOT NULL) or "
         "(holiday_type='company' AND mode_company_id IS NOT NULL))",
         "The employee, department, company or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('duration_check', "CHECK ( number_of_days == 0 )", "The number of days must be greater than 0."),
        ('number_per_interval_check', "CHECK(number_per_interval > 0)",
         "The number per interval should be greater than 0"),
        ('interval_number_check', "CHECK(interval_number > 0)", "The interval number should be greater than 0"),
    ]


class LeavesAllocation(models.Model):
    _name = "hr.leave.allocation.method"
    _rec_name = 'name'

    name = fields.Char('Name', required=True, help='Leave Method name')
    type_state = fields.Selection(string="Type", selection=[('all', 'All'), ('two', '5 Yours'), ], required=True, )
    all_year = fields.Float(string="All Years", required=False, )
    first_year = fields.Float(string="First Years", required=False, )
    second_year = fields.Float(string="Second Years", required=False, )
