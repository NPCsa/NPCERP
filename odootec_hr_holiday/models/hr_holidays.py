# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning
from datetime import date, datetime, timedelta, time as datetime_time
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
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False,
                                 default=lambda self: self.env.user.company_id)

    @api.multi
    def action_refuse(self):
        for record in self:
            if record.is_reconciled:
                raise Warning(_('You can not refuse leave reconciled'))
        return super(HrHolidays, self).action_refuse()

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
        reconcile = False
        return_work = False
        constrain_check = False
        if values.get('is_reconciled') != None and (values.get('is_reconciled') or not values.get('is_reconciled')):
            reconcile = True
        if values.get('return_date') != None and (values.get('return_date') or not values.get('return_date')):
            return_work = True
        if reconcile or return_work:
            constrain_check = True
        for record in self:
            if not constrain_check:
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
                else:
                    raise Warning(_('No Contract for This Employee or Check the Starting Date in Contract'))
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

        else:
            raise Warning(_('No Contract for This Employee or Check the Starting Date in Contract'))
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

        def daterangeleave(start_date, end_date):
            for n in range(int((end_date - start_date).days + 1)):
                yield start_date + timedelta(n)

        vals = {}
        employee_obj = self.env['hr.employee'].search([('eligible', '=', True), ('calculate_type', '=', 'automatic')])
        for emp in employee_obj:
            leave_days = 0.0
            if emp.eligible and emp.holiday_line_ids:
                for line in emp.holiday_line_ids:
                    if line.allocation_range == 'month':
                        allocate_date = str((datetime.now() + relativedelta(day=1)))[:10]
                        date_from_dt = datetime.now() - relativedelta(months=1) + relativedelta(day=1)
                        date_to_dt = datetime.now() - relativedelta(months=1) + relativedelta(day=31)
                        date_from = fields.Datetime.from_string(str(date_from_dt)).date()
                        date_to = fields.Datetime.from_string(str(date_to_dt)).date()
                        allocate_ids = self.env['hr.leave.allocation'].sudo().search([
                            ('last_allocation_date', '=', allocate_date),
                            ('employee_id', '=', emp.id),
                            ('holiday_status_id', '=', line.leave_status_id.id)])
                        day_from = datetime.combine(fields.Date.from_string(date_from), datetime_time.min)
                        day_to = datetime.combine(fields.Date.from_string(date_to), datetime_time.max)
                        holiday_id = []
                        day_leave_intervals = emp.list_leaves(day_from, day_to,
                                                              calendar=emp.resource_calendar_id)
                        for day, hours, leave in day_leave_intervals:
                            holiday = leave.holiday_id
                            holiday_id.append(holiday.id)
                        holiday_id = list(set(holiday_id))
                        holidays = self.env['hr.leave'].browse(holiday_id)
                        date_from = fields.Datetime.from_string(date_from)
                        date_to = fields.Datetime.from_string(date_to)
                        for lline in holidays:
                            if lline.return_date:
                                r_date_from = fields.Datetime.from_string(lline.date_from)
                                r_date_to = fields.Datetime.from_string(lline.return_date)
                                if r_date_from and r_date_to:
                                    for date in daterangeleave(r_date_from, r_date_to):
                                        if date_from <= date <= date_to:
                                            leave_days += 1
                            else:
                                r_date_from = fields.Datetime.from_string(lline.date_from)
                                r_date_to = date_to
                                if r_date_from and r_date_to:
                                    for date in daterangeleave(r_date_from, r_date_to):
                                        if date_from <= date <= date_to:
                                            leave_days += 1
                        clause_final = [('state', 'in', ['validate', 'validate1']),
                                        ('return_date', '!=', False),
                                        ('date_to', '<', date_from), ('employee_id', '=', self.employee_id.id)]
                        request_leaves = self.env['hr.leave'].search(clause_final)
                        if request_leaves:
                            for hl in request_leaves:
                                hr_date_from = fields.Datetime.from_string(hl.date_from)
                                hr_date_to = fields.Datetime.from_string(hl.return_date)
                                if hr_date_from and hr_date_to:
                                    for date in daterangeleave(hr_date_from, hr_date_to):
                                        if date_from <= date <= date_to:
                                            leave_days += 1

                        clause_final = [('state', 'in', ['validate', 'validate1']),
                                        ('return_date', '=', False),
                                        ('date_to', '<', date_from), ('employee_id', '=', self.employee_id.id)]
                        request_leaves = self.env['hr.leave'].search(clause_final)
                        if request_leaves:
                            for hl in request_leaves:
                                r_date_from = fields.Datetime.from_string(hl.date_from)
                                r_date_to = date_to
                                if r_date_from and r_date_to:
                                    for date in daterangeleave(r_date_from, r_date_to):
                                        if date_from <= date <= date_to:
                                            leave_days += 1
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
                                days = date_to_dt.day - joining_date.day + 1
                                days_to_allocate = (line.days_to_allocate / 30) * (days - leave_days)
                            else:
                                days = date_to_dt.day - date_from_dt.day + 1
                                days_to_allocate = (line.days_to_allocate / days) * (days - leave_days)
                            vals = {
                                'name': 'Monthly Allocation of ' + line.leave_status_id.name + ' Leaves',
                                'number_of_days': days_to_allocate,
                                'last_allocation_date': allocate_date,
                                'employee_id': emp.id,
                                'company_id': emp.company_id.id,
                                'holiday_status_id': line.leave_status_id.id
                            }

                    if line.allocation_range == 'year':
                        allocate_date = str((datetime.now() + relativedelta(month=1) + relativedelta(day=1)))[:10]
                        date_to_dt = datetime.now() - relativedelta(years=1) \
                                     + relativedelta(month=12) + relativedelta(day=31)
                        date_from_dt = datetime.now() - relativedelta(years=1) + relativedelta(month=1) \
                                       + relativedelta(day=1)
                        allocate_ids = self.env['hr.leave.allocation'].search(
                            [('last_allocation_date', '=', allocate_date),
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
                                        (date_to_dt - joining_date).days + 1)
                            else:
                                days_to_allocate = line.days_to_allocate
                            vals = {
                                'name': 'Yearly Allocation of ' + line.leave_status_id.name + ' Leaves',
                                'number_of_days': days_to_allocate,
                                'last_allocation_date': allocate_date,
                                'employee_id': emp.id,
                                'company_id': emp.company_id.id,
                                'holiday_status_id': line.leave_status_id.id,
                            }
                    if vals:
                        leave = self.env['hr.leave.allocation'].create(vals)
                        leave.action_approve()
                        if leave.holiday_status_id.double_validation:
                            leave.action_validate()
                        emp.update({'last_allocation_date': allocate_date})


class LeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    last_allocation_date = fields.Date(string="Allocation Date", required=False,
                                       default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_change = fields.Boolean(string="Make Allocation Change", )

    leave_on_employee = fields.Boolean(string="Leave On Employee", compute='_compute_leave_on_employee')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False,
                                 default=lambda self: self.env.user.company_id)

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
