import time
from odoo import exceptions, models, fields, api, _
from datetime import datetime
from .. import utils
from odoo.exceptions import Warning


class AccountMove(models.Model):
    _inherit = 'account.move'

    termination_id = fields.Many2one('hr.termination', 'Termination', help='Termination Record')


class Termination(models.Model):
    _name = 'hr.termination'
    _rec_name = 'termination_code'

    @api.one
    @api.depends('total_deserve', 'deserve_salary_amount', 'add_value', 'loan_value', 'ded_value')
    def _compute_total_deserve(self):
        for termination in self:
            termination.total_deserve_amount = termination.total_deserve + termination.deserve_salary_amount + termination.add_value - termination.loan_value - termination.ded_value

    @api.multi
    def get_contracts(self):
        contract_obj = self.env['hr.contract']
        contract_ids = []
        for termination in self:
            date_to = termination.job_ending_date
            date_from = termination.employee_id.contract_id.date_start
            employee = termination.employee_id
            clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
            # OR if it starts between the given dates
            clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
            # OR if it starts before the date_from and finish after the date_end (or never finish)
            clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False),
                        ('date_end', '>=', date_to)]
            clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open'), '|',
                            '|'] + clause_1 + clause_2 + clause_3
            contract_ids = contract_obj.search(clause_final)
        return contract_ids

    @api.multi
    def calculate_vacation(self):
        holiday_obj = self.env['hr.leave']
        holiday_records = holiday_obj.search([('employee_id', '=', self.employee_id.id),
                                              ('state', '=', 'validate')])
        total_leave = 0
        total_leave_taken = 0
        if holiday_records:
            for holiday in holiday_records:
                total_leave_taken += holiday.number_of_days
        if total_leave > total_leave_taken:
            return total_leave - total_leave_taken
        else:
            return 0

    is_clearance = fields.Boolean(string="Is Clearance", )
    termination_code = fields.Char('Termination NO', readonly=True, states={'draft': [('readonly', False)]},
                                   default='Termination')
    date = fields.Date('Application Date', readonly=True, states={'draft': [('readonly', False)]},
                       default=fields.Date.today())
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    employee_code = fields.Char(related='employee_id.employee_id')
    contract_id = fields.Many2one('hr.contract', 'Contract', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    job_id = fields.Many2one('hr.job', 'Job Title', readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    job_ending_date = fields.Date('Job Ending Date', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]}, defualt=fields.Date.today())
    hire_date = fields.Date('Hire Date', readonly=True, required=True, states={'draft': [('readonly', False)]})
    approved_by = fields.Many2one('res.users', 'Approved By', readonly=True, states={'draft': [('readonly', False)]})
    approval_date = fields.Date('Approval Date', readonly=True, states={'draft': [('readonly', False)]},
                                default=fields.Date.today)
    loan_value = fields.Float('Loan Value')
    ded_value = fields.Float('Deduction Value')
    add_value = fields.Float('Addition Value')
    total_deserve = fields.Float('End Of Service Amount', compute='_calculate_severance', readonly=True,
                                 help="Calculation By Basic Salary + Housing Allowance + Transportation Allowance")
    total_deserve_amount = fields.Float('Total Deserved', compute='_compute_total_deserve', readonly=True)
    from_years = fields.Float('From Years', readonly=True, states={'draft': [('readonly', False)]})
    to_years = fields.Float('To Years', readonly=True, states={'draft': [('readonly', False)]})
    basic_salary = fields.Float('Total Salary', readonly=True, states={'draft': [('readonly', False)]})
    min_months = fields.Float('Min Months', readonly=True, states={'draft': [('readonly', False)]})
    working_period = fields.Float('Working Period', readonly=True, states={'draft': [('readonly', False)]})
    period_in_years = fields.Float('Period in Years', readonly=True, states={'draft': [('readonly', False)]})
    vacation_days = fields.Float('Vacation Days', readonly=True, states={'draft': [('readonly', False)]})
    salary_amount = fields.Float('Salary Amount', readonly=True, states={'draft': [('readonly', False)]})
    deserve_salary_amount = fields.Float('Leaves Amount', readonly=True, states={'draft': [('readonly', False)]},
                                         help="Calculation By (Total Salary - Transportation Allowance)/ 30 ")
    move_id = fields.Many2one('account.move', 'Journal Entry', help='Journal Entry for Termination')
    payment_method = fields.Many2one('termination.payments', 'Payment Method', help='Payment method for termination')
    journal_id = fields.Many2one('account.journal', 'Journal', help='Journal for journal entry')
    notes = fields.Text(string="Notes", required=False, )
    state = fields.Selection([('draft', _('Draft')),
                              ('review', _('Review')),
                              ('cancel', _('Cancelled')),
                              ('approved', _('First Approve')),
                              ('approved2', _('Second Approve'))
                              ], _('Status'), readonly=True, copy=False, default='draft',
                             help=_("Gives the status of the Termination"), select=True)

    eos_reason = fields.Selection([('1', 'Expiration of the contract'),
                                   ('10', 'Contract termination agreement between the employee and the employer'),
                                   ('11', 'Contract terminated by the employer'),
                                   ('12', 'Employee leaving the work for one of the cases mentioned in Article (81)'),
                                   ('13', 'Employee leaving the work as a result of force majeure'),
                                   ('14',
                                    'Female employee termination of an employment contract within 6 months of the marriage contract'),
                                   ('15',
                                    'Female employee termination of an employment contract within 3 months of the birth giving'),
                                   ('2',
                                    'Contract terminated by the employer for one of the cases mentioned in Article (80)'),
                                   ('20', 'Contract termination by the employee'),
                                   ('21', 'Leaving work for cases other than those mentioned in Article (81)'),
                                   ('3', 'Employee resignation')], string='EOS Reason')

    @api.model
    def create(self, vals):
        termination_code = self.env['ir.sequence'].get('hr.termination.code')
        vals['termination_code'] = termination_code
        return super(Termination, self).create(vals)

    @api.multi
    def get_employee_balance_leave(self):
        for holiday in self:
            leave_days = 0.0
            if holiday.employee_id.joining_date and holiday.job_ending_date and holiday.employee_id.last_allocation_date:
                today = datetime.strptime(str(holiday.job_ending_date), '%Y-%m-%d')
                join_date = datetime.strptime(str(holiday.employee_id.joining_date), '%Y-%m-%d')
                last_allocation_date = datetime.strptime(str(holiday.employee_id.last_allocation_date), '%Y-%m-%d')
                diff = today.date() - join_date.date()
                allocation_days = (today.date() - last_allocation_date.date()).days
                service_period = round((diff.days / 365) * 12, 2)
                allocation_method = holiday.employee_id.allocation_method
                day_allocate_lt = 0.0
                day_allocate_gt = 0.0
                day_allocate_eq = 0.0
                if allocation_method:
                    if allocation_method.type_state == 'two':
                        day_allocate_lt = allocation_method.first_year / (365 - allocation_method.first_year)
                        day_allocate_gt = allocation_method.second_year / (365 - allocation_method.second_year)
                        if allocation_days:
                            if service_period <= 60:
                                leave_days = allocation_days * day_allocate_lt
                            else:

                                allocate_days = (last_allocation_date.date() - join_date.date()).days
                                if allocate_days >= 1825:
                                    leave_days = allocation_days * day_allocate_gt
                                else:
                                    day_to = 0
                                    for n in range(0, allocation_days + 1):

                                        if allocate_days <= 1825:
                                            allocate_days += 1
                                            day_to += 1
                                        else:

                                            days_gt = allocation_days - day_to
                                            leave_days = (days_gt * day_allocate_gt) + (day_to * day_allocate_lt)
                                            break
                    if allocation_method.type_state == 'all':
                        day_allocate_eq = allocation_method.all_year / (365 - allocation_method.all_year)
                        if allocation_days:
                            leave_days = allocation_days * day_allocate_eq
            return leave_days

    @api.onchange('job_ending_date')
    def onchange_ending_date(self):
        if self.employee_id:
            remaining_vacation = self.employee_id.remaining_leaves + self.get_employee_balance_leave()
            self.vacation_days = remaining_vacation

    @api.onchange('employee_id', 'job_ending_date')
    def onchange_employee_id(self):
        if self.employee_id:
            vals = {'domain': {'contract_id': False}}
            self.job_id = self.employee_id.job_id.id
            self.hire_date = self.employee_id.joining_date
            remaining_vacation = self.employee_id.remaining_leaves + self.get_employee_balance_leave()
            self.vacation_days = remaining_vacation
            contracts = self.get_contracts()
            li = []
            if contracts:
                for i in contracts:
                    li.append(i.id)
                vals['domain'].update({'contract_id': [('id', 'in', li)]})
            return vals

    @api.onchange('contract_id', 'employee_id', 'payment_method')
    def _onchange_contract_id(self):
        for record in self:
            salary_amount = 0.0
            basic_salary = 0.0
            if record.contract_id and record.payment_method:
                basic = record.contract_id.wage
                for field in record.payment_method.leave_rules:
                    if field.name == 'wage':
                        salary_amount += record.contract_id[field.name]
                    elif field.name == 'transportation_allowance':
                        salary_amount += (basic * (
                                record.contract_id.transportation_allowance / 100) if record.contract_id.is_trans else record.contract_id.transportation_allowance)
                    elif field.name == 'housing_allowance':
                        salary_amount += (basic * (
                                record.contract_id.housing_allowance / 100) if record.contract_id.is_house else record.contract_id.housing_allowance)
                    elif field.name == 'mobile_allowance':
                        salary_amount += (basic * (
                                record.contract_id.mobile_allowance / 100) if record.contract_id.is_mobile else record.contract_id.mobile_allowance)
                    elif field.name == 'overtime_allowance':
                        salary_amount += (basic * (
                                record.contract_id.overtime_allowance / 100) if record.contract_id.is_over else record.contract_id.overtime_allowance)
                    elif field.name == 'work_allowance':
                        salary_amount += (basic * (
                                record.contract_id.work_allowance / 100) if record.contract_id.is_work else record.contract_id.work_allowance)
                    elif field.name == 'reward':
                        salary_amount += (basic * (
                                record.contract_id.reward / 100) if record.contract_id.is_reward else record.contract_id.reward)
                    elif field.name == 'ticket_allowance':
                        salary_amount += (basic * (
                                record.contract_id.ticket_allowance / 100) if record.contract_id.is_ticket else record.contract_id.ticket_allowance)
                    elif field.name == 'food_allowance':
                        salary_amount += (basic * (
                                record.contract_id.food_allowance / 100) if record.contract_id.is_food else record.contract_id.food_allowance)
                    elif field.name == 'other_allowance':
                        salary_amount += (basic * (
                                record.contract_id.other_allowance / 100) if record.contract_id.is_other else record.contract_id.other_allowance)
                for field_id in record.payment_method.field_ids:
                    if field_id.name == 'wage':
                        basic_salary += record.contract_id[field_id.name]
                    elif field_id.name == 'transportation_allowance':
                        basic_salary += (basic * (
                                record.contract_id.transportation_allowance / 100) if record.contract_id.is_trans else record.contract_id.transportation_allowance)
                    elif field_id.name == 'housing_allowance':
                        basic_salary += (basic * (
                                record.contract_id.housing_allowance / 100) if record.contract_id.is_house else record.contract_id.housing_allowance)
                    elif field_id.name == 'mobile_allowance':
                        basic_salary += (basic * (
                                record.contract_id.mobile_allowance / 100) if record.contract_id.is_mobile else record.contract_id.mobile_allowance)
                    elif field_id.name == 'overtime_allowance':
                        basic_salary += (basic * (
                                record.contract_id.overtime_allowance / 100) if record.contract_id.is_over else record.contract_id.overtime_allowance)
                    elif field_id.name == 'work_allowance':
                        basic_salary += (basic * (
                                record.contract_id.work_allowance / 100) if record.contract_id.is_work else record.contract_id.work_allowance)
                    elif field_id.name == 'reward':
                        basic_salary += (basic * (
                                record.contract_id.reward / 100) if record.contract_id.is_reward else record.contract_id.reward)
                    elif field_id.name == 'ticket_allowance':
                        basic_salary += (basic * (
                                record.contract_id.ticket_allowance / 100) if record.contract_id.is_ticket else record.contract_id.ticket_allowance)
                    elif field_id.name == 'food_allowance':
                        basic_salary += (basic * (
                                record.contract_id.food_allowance / 100) if record.contract_id.is_food else record.contract_id.food_allowance)
                    elif field_id.name == 'other_allowance':
                        basic_salary += (basic * (
                                record.contract_id.other_allowance / 100) if record.contract_id.is_other else record.contract_id.other_allowance)

            record.salary_amount = salary_amount
            record.basic_salary = basic_salary
            remaining_vacation = record.employee_id.remaining_leaves + record.get_employee_balance_leave()
            record.vacation_days = remaining_vacation
            record.deserve_salary_amount = (salary_amount / 30) * remaining_vacation

    @api.onchange('vacation_days')
    def _onchange_vacation(self):
        if self.vacation_days:
            self.deserve_salary_amount = (self.salary_amount / 30) * self.vacation_days

    @api.onchange('job_ending_date', 'hire_date')
    def _onchange_dates(self):
        if self.job_ending_date and self.hire_date:
            start_date = datetime.strptime(str(self.hire_date), '%Y-%m-%d')
            end_date = datetime.strptime(str(self.job_ending_date), '%Y-%m-%d')
            months = utils.months_between(start_date, end_date)
            years = utils.years_between(start_date, end_date)
            self.working_period = months
            self.period_in_years = years

    @api.one 
    @api.depends('working_period', 'eos_reason', 'basic_salary')
    def _calculate_severance(self):
        total_severance = 0
        pass_duration = 0
        if self.eos_reason in ['2', '20', '21']:  # for the zeros issues
            self.total_deserve = 0
        elif self.eos_reason in ['1', '10', '11', '12', '13', '14', '15']:  # for the normal issues
            if self.working_period < 60:
                self.total_deserve = self.working_period * 1 / 24 * self.basic_salary
            else:
                total_severance = 60 * 1 / 24 * self.basic_salary
                pass_duration = self.working_period - 60
                total_severance = total_severance + (pass_duration * 1 / 12 * self.basic_salary)
                self.total_deserve = total_severance
        elif self.eos_reason == '3':  # Worst case resignation
            if self.working_period < 24:
                self.total_deserve = 0
            elif self.working_period < 60:
                self.total_deserve = self.working_period * 1 / 24 * 1 / 3 * self.basic_salary
            elif self.working_period < 120:
                total_severance = 60 * 1 / 24 * 2 / 3 * self.basic_salary
                pass_duration = self.working_period - 60
                self.total_deserve = total_severance + (pass_duration * 1 / 12 * 2 / 3 * self.basic_salary)
            else:
                total_severance = 60 * 1 / 24 * self.basic_salary
                pass_duration = self.working_period - 60
                self.total_deserve = total_severance + (pass_duration * 1 / 12 * self.basic_salary)

    @api.multi
    def button_review(self):
        self.state = 'review'

    @api.multi
    def button_approve(self):
        self.approved_by = self.env.user.id
        self.state = 'approved'
        self.contract_id.end_of_service = self.contract_id.date_end
        self.contract_id.date_end = self.job_ending_date
        self.contract_id.is_terminated = True

    @api.multi
    def button_cancel(self):
        if self.state not in ['approved', 'approved2']:
            self.state = 'cancel'
        elif self.move_id and self.move_id.state == 'draft':
            self.contract_id.date_end = self.contract_id.end_of_service
            self.contract_id.is_terminated = False
            self.contract_id.end_of_service = False
            self.move_id.unlink()
            self.state = 'cancel'
        elif self.state in ['approved']:
            self.contract_id.date_end = self.contract_id.end_of_service
            self.contract_id.is_terminated = False
            self.state = 'cancel'
        else:
            raise Warning(_('You cannot delete a termination document'
                            ' which is posted Entries!'))

    @api.multi
    def unlink(self):
        for termination in self:
            if termination.state not in ['draft', 'review', 'cancel']:
                raise Warning(_('You cannot delete a termination document'
                                ' which is not draft or review or cancelled!'))
        return super(Termination, self).unlink()

    @api.multi
    def validate_termination(self):

        if self.payment_method:
            move_obj = self.env['account.move']
            timenow = time.strftime('%Y-%m-%d')

            line_ids = []
            name = _('Termination for ') + self.employee_id.name
            move = {
                'narration': name,
                'ref': self.termination_code,
                'date': self.approval_date or timenow,
                'termination_id': self.id,
                'journal_id': self.journal_id.id,
            }

            total_amount = self.total_deserve_amount
            eos_amount = self.total_deserve
            leave_amount = self.deserve_salary_amount
            add_amount = self.add_value
            loan_amount = self.loan_value
            ded_amount = self.ded_value
            debit_account_id = self.payment_method.debit_account_id.id or False
            credit_account_id = self.payment_method.credit_account_id.id or False
            loan_debit_account_id = self.payment_method.loan_debit_account_id.id or False
            loan_credit_account_id = self.payment_method.loan_credit_account_id.id or False
            leave_debit_account_id = self.payment_method.leave_debit_account_id.id or False
            leave_credit_account_id = self.payment_method.leave_credit_account_id.id or False
            ded_debit_account_id = self.payment_method.ded_debit_account_id.id or False
            ded_credit_account_id = self.payment_method.ded_credit_account_id.id or False
            add_debit_account_id = self.payment_method.add_debit_account_id.id or False
            add_credit_account_id = self.payment_method.add_credit_account_id.id or False

            if not self.payment_method:
                raise Warning(_('Please Set payment method'))

            if total_amount <= 0:
                raise Warning(_('Please Set Amount'))

            if not self.journal_id:
                raise Warning(_('Please Set Journal'))
            if not self.employee_id.address_home_id:
                raise Warning(_('Please Set Related Partner For Employee'))

            partner_id = False
            if self.employee_id.address_home_id:
                partner_id = self.employee_id.address_home_id.id

            if eos_amount:
                if not credit_account_id or not debit_account_id:
                    raise Warning(_('Please Set EOS credit/debit account '))
                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Termination',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': eos_amount,
                        'credit': 0.0,
                    })
                    line_ids.append(debit_line)

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Termination',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': eos_amount,
                    })
                    line_ids.append(credit_line)
            if leave_amount:
                if not leave_credit_account_id or not leave_debit_account_id:
                    raise Warning(_('Please Set Leave credit/debit account '))
                if leave_debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Leaves',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': leave_debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': leave_amount,
                        'credit': 0.0,
                    })
                    line_ids.append(debit_line)

                if leave_credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Leaves',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': leave_credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': leave_amount,
                    })
                    line_ids.append(credit_line)
            if add_amount:
                if not add_credit_account_id or not add_debit_account_id:
                    raise Warning(_('Please Set Addition credit/debit account '))
                if add_debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Addition',
                        'date': self.approval_date or timenow,
                        'partner_id': False,
                        'account_id': add_debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': add_amount,
                        'credit': 0.0,
                    })
                    line_ids.append(debit_line)

                if add_credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Addition',
                        'date': self.approval_date or timenow,
                        'partner_id': False,
                        'account_id': add_credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': add_amount,
                    })
                    line_ids.append(credit_line)
            if loan_amount:
                if not loan_credit_account_id or not loan_debit_account_id:
                    raise Warning(_('Please Set Loan credit/debit account '))
                if loan_debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Loan',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': loan_debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': loan_amount,
                        'credit': 0.0,
                    })
                    line_ids.append(debit_line)

                if loan_credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Loan',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': loan_credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': loan_amount,
                    })
                    line_ids.append(credit_line)
            if ded_amount:
                if not ded_credit_account_id or not ded_debit_account_id:
                    raise Warning(_('Please Set Deduction credit/debit account '))
                if ded_debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Deduction',
                        'date': self.approval_date or timenow,
                        'partner_id': False,
                        'account_id': ded_debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': ded_amount,
                        'credit': 0.0,
                    })
                    line_ids.append(debit_line)

                if ded_credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Deduction',
                        'date': self.approval_date or timenow,
                        'partner_id': False,
                        'account_id': ded_credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': ded_amount,
                    })
                    line_ids.append(credit_line)

            move.update({'line_ids': line_ids})
            move_id = move_obj.create(move)

            self.write(
                {'move_id': move_id.id, 'state': 'approved2', })
            # move_id.post()
        return True

    @api.multi
    def open_entries(self):
        context = dict(self._context or {}, search_default_termination_id=self.ids, default_termination_id=self.ids)
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', '=', self.move_id.id)],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': context,
        }


class TerminationsPayments(models.Model):
    _name = "termination.payments"

    name = fields.Char('Name', required=True, help='Payment name')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    debit_account_id = fields.Many2one('account.account', 'EOS Debit Account', required=False,
                                       help='EOS Debit account for journal entry')
    credit_account_id = fields.Many2one('account.account', 'EOS Credit Account', required=False,
                                        help='EOS Credit account for journal entry')
    loan_debit_account_id = fields.Many2one('account.account', 'Loan Debit Account', required=False,
                                            help='Loan Debit account for journal entry')
    loan_credit_account_id = fields.Many2one('account.account', 'Loan Credit Account', required=False,
                                             help='Loan Credit account for journal entry')
    leave_debit_account_id = fields.Many2one('account.account', 'Leave Debit Account', required=False,
                                             help='Leave Debit account for journal entry')
    leave_credit_account_id = fields.Many2one('account.account', 'Leave Credit Account', required=False,
                                              help='Leave Credit account for journal entry')
    ded_debit_account_id = fields.Many2one('account.account', 'Deduction Debit Account', required=False,
                                           help='Deduction Debit account for journal entry')
    ded_credit_account_id = fields.Many2one('account.account', 'Deduction Credit Account', required=False,
                                            help='Deduction Credit account for journal entry')
    add_debit_account_id = fields.Many2one('account.account', 'Addition Debit Account', required=False,
                                           help='Addition Debit account for journal entry')
    add_credit_account_id = fields.Many2one('account.account', 'Addition Credit Account', required=False,
                                            help='Addition Credit account for journal entry')
    field_ids = fields.Many2many(comodel_name="ir.model.fields", relation="termination_field_rel",
                                 string="End Of Service Rules",
                                 domain=[('model_id', '=', 'hr.contract'), ('ttype', 'in', ['float', 'monetary'])])
    leave_rules = fields.Many2many(comodel_name="ir.model.fields", relation="leaves_field_rel", string="Leave Rules",
                                   domain=[('model_id', '=', 'hr.contract'), ('ttype', 'in', ['float', 'monetary'])])


class HrContract(models.Model):
    _inherit = "hr.contract"

    end_of_service = fields.Date('Original End Date')
    is_terminated = fields.Boolean('Terminated')
    trial_date_start = fields.Date()
    working_hours = fields.Float()
