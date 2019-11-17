# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, Warning, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    termination_leave_id = fields.Many2one('hr.holiday.termination', 'Settlement', help='Settlement Record')


class Settlement(models.Model):
    _name = 'hr.holiday.termination'
    _rec_name = 'termination_code'
    _description = 'New Settlement'

    termination_code = fields.Char('Settlement NO', readonly=True, states={'draft': [('readonly', False)]},
                                   default='Settlement')
    date = fields.Date('Application Date', readonly=True, states={'draft': [('readonly', False)]},
                       default=fields.Date.today())
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    employee_code = fields.Char(related='employee_id.employee_id')
    reconcile_date = fields.Date(string="Reconcile Date", required=True)
    reconcile_type = fields.Selection(string="Reconcile Type",
                                      selection=[('request', 'Leave Request'), ('balance', 'Balance'),
                                                 ('both', 'Both'), ], required=True, default='request')
    balance_days = fields.Float(string="Reconcile Days", required=False, )
    employee_balance_days = fields.Float(string="Current Balance Days", required=False, compute='_get_vacation_days')
    vacation_days = fields.Float('Vacation Days', required=False, compute='_get_vacation_days')
    vacation_days_comp = fields.Float('vacation days comp', required=False, )
    balance_days_comp = fields.Float('balance days comp', required=False, )
    contract_id = fields.Many2one('hr.contract', 'Contract', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    job_id = fields.Many2one('hr.job', 'Job Title', readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    approved_by = fields.Many2one('res.users', 'Approved By', default=lambda self: self.env.user, readonly=True,
                                  states={'draft': [('readonly', False)]})
    approval_date = fields.Date('Approval Date', readonly=True, states={'draft': [('readonly', False)]})
    salary_amount = fields.Float('Salary Amount', readonly=True, states={'draft': [('readonly', False)]},
                                 compute='_onchange_contract_id')
    leave_amount = fields.Float(string="Leave Amount", required=False, compute='_onchange_contract_id')
    ticket_amount = fields.Float(string="Ticket Amount", required=False, )
    total_amount = fields.Float(string="Total Amount", required=False, compute='_compute_total_amount')
    move_id = fields.Many2one('account.move', 'Journal Entry', help='Journal Entry for Settlement')
    leave_reconcile_id = fields.Many2one('hr.leave.allocation', 'Leave Reconcile')
    payment_method = fields.Many2one('termination.leave.payments', 'Payment Method',
                                     help='payment method for Settlement')
    journal_id = fields.Many2one('account.journal', 'Journal', help='Journal for journal entry')
    notes = fields.Text(string="Notes", required=False, )
    emp_member = fields.Integer(string="Family Member", readonly=True, states={'draft': [('readonly', False)]})
    emp_city = fields.Char(string="Employee City", readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', _('Draft')),
                              ('review', _('Review')),
                              ('cancel', _('Cancelled')),
                              ('approved', _('First Approve')),
                              ('approved2', _('Second Approve'))
                              ], _('Status'), readonly=True, copy=False, default='draft',
                             help=_("Gives the status of the Settlement"), select=True)

    @api.constrains('balance_days', 'reconcile_date')
    def _constrain_balance_days(self):
        for record in self:
            if record.balance_days > record.employee_id.remaining_allocate_leaves:
                raise ValidationError("You Can not reconcile days greater than balance of Employee")
            reconciles = self.search([('reconcile_date', '>=', record.reconcile_date), ('state', '!=', 'cancel'),
                                      ('employee_id', '<=', record.employee_id.id)])
            if len(reconciles) > 1:
                raise ValidationError("You Can not reconcile more for same Time")

    @api.multi
    def button_cancel(self):
        if self.state not in ['approved', 'approved2']:
            self.state = 'cancel'
        elif self.move_id and self.move_id.state == 'draft':
            leave_type = self.employee_id.holiday_line_ids.mapped('leave_status_id').ids
            domain = [('holiday_status_id', 'in', leave_type), ('state', '=', 'validate'),
                      ('request_date_from', '<=', self.reconcile_date), ('reconcile_option', '=', 'yes'),
                      ('is_reconciled', '=', True)]
            leaves = self.env['hr.leave'].search(domain)
            for l in leaves:
                l.is_reconciled = False
            if self.leave_reconcile_id:
                self.leave_reconcile_id.action_refuse()
                self.leave_reconcile_id.action_draft()
                self.leave_reconcile_id.unlink()
            self.move_id.unlink()
            self.state = 'cancel'
        else:
            raise Warning(_('You cannot delete a termination document'
                            ' which is posted Entries!'))

    @api.one
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.leave_amount + record.ticket_amount

    @api.multi
    def button_review(self):
        self.write({'state': 'review'})

    @api.multi
    def button_approve(self):
        termination_code = self.env['ir.sequence'].get('hr.termination.leave.code')
        self.write({'termination_code': termination_code, 'state': 'approved'})

    @api.onchange('reconcile_type', 'reconcile_date')
    def _compute_vacation_days(self):
        for line in self:
            line.balance_days_comp = self.employee_id.remaining_allocate_leaves
            leave_type = line.employee_id.holiday_line_ids.mapped('leave_status_id').ids
            domain = [('holiday_status_id', 'in', leave_type), ('state', '=', 'validate'),
                      ('employee_id', '=', line.employee_id.id),
                      ('request_date_from', '<=', line.reconcile_date), ('reconcile_option', '=', 'yes'),
                      ('is_reconciled', '=', False)]
            leave = self.env['hr.leave'].search(domain)
            leave_days = sum([l.number_of_days for l in leave])
            line.vacation_days_comp = leave_days

    @api.onchange('reconcile_type', 'reconcile_date')
    def _get_vacation_days(self):
        for record in self:
            record.employee_balance_days = record.balance_days_comp
            record.vacation_days = record.vacation_days_comp

    @api.multi
    def validate_termination(self):
        if self.reconcile_type in ['balance', 'both'] and self.balance_days:
            leave_type = self.employee_id.holiday_line_ids.mapped('leave_status_id').ids[0]
            vals = {
                'name': 'Reconcile Balance Days',
                'employee_id': self.employee_id.id,
                'holiday_status_id': leave_type,
                'last_allocation_date': self.reconcile_date,
                'date_change': True,
                'number_of_days': self.balance_days * -1,
            }
            leave = self.env['hr.leave.allocation'].create(vals)
            leave.action_approve()
            if leave.holiday_status_id.double_validation:
                leave.action_validate()
            self.write({'leave_reconcile_id': leave.id})

        leave_type = self.employee_id.holiday_line_ids.mapped('leave_status_id').ids
        domain = [('holiday_status_id', 'in', leave_type), ('state', '=', 'validate'),
                  ('request_date_from', '<=', self.reconcile_date), ('reconcile_option', '=', 'yes'),
                  ('is_reconciled', '=', False)]
        leaves = self.env['hr.leave'].search(domain)
        for l in leaves:
            l.is_reconciled = True
        move_obj = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')
        line_ids = []
        name = _('Settlement for ') + self.employee_id.name
        move = {
            'narration': name,
            'ref': self.termination_code,
            'date': self.approval_date or timenow,
            'termination_leave_id': self.id,
            'journal_id': self.journal_id.id,
        }

        leave_amount = self.leave_amount
        ticket_amount = self.ticket_amount
        ticket_debit_account_id = self.payment_method.ticket_debit_account_id.id or False
        ticket_credit_account_id = self.payment_method.ticket_credit_account_id.id or False
        leave_debit_account_id = self.payment_method.leave_debit_account_id.id or False
        leave_credit_account_id = self.payment_method.leave_credit_account_id.id or False

        if not self.journal_id:
            raise Warning(_('Please Set Journal'))

        if not self.employee_id.address_home_id:
            raise Warning(_('Please Set Related Partner For Employee'))

        partner_id = False
        if self.employee_id.address_home_id:
            partner_id = self.employee_id.address_home_id.id

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
        if ticket_amount:
            if not ticket_debit_account_id or not ticket_credit_account_id:
                raise Warning(_('Please Set Ticket credit/debit account '))
            if ticket_debit_account_id:
                debit_line = (0, 0, {
                    'name': 'Ticket',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': ticket_debit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': ticket_amount,
                    'credit': 0.0,
                })
                line_ids.append(debit_line)

            if ticket_credit_account_id:
                credit_line = (0, 0, {
                    'name': 'Ticket',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': ticket_credit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': 0.0,
                    'credit': ticket_amount,
                })
                line_ids.append(credit_line)

        move.update({'line_ids': line_ids})
        move_id = move_obj.create(move)

        self.write(
            {'move_id': move_id.id, 'state': 'approved2', })
        # move_id.post()
        return True

    @api.multi
    def get_contracts(self):
        contract_obj = self.env['hr.contract']
        contract_ids = []
        for termination in self:
            employee = termination.employee_id
            clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open')]
            contract_ids = contract_obj.search(clause_final)
        return contract_ids

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.contract_id = False
        if self.employee_id:
            vals = {'domain': {'contract_id': False}}
            self.job_id = self.employee_id.job_id.id
            self.emp_city = self.employee_id.emp_city
            member = 0
            if self.employee_id.family_member_ids:
                member = len(self.employee_id.family_member_ids)
            self.emp_member = member
            contract_ids = self.get_contracts()
            if contract_ids:
                contracts = sorted(contract_ids, key=lambda x: x.date_start, reverse=True)
                self.contract_id = contracts[0].id
            return vals

    @api.onchange('contract_id', 'employee_id', 'payment_method', 'vacation_days', 'balance_days')
    def _onchange_contract_id(self):
        for record in self:
            salary_amount = 0.0
            if record.contract_id and record.payment_method:
                basic = record.contract_id.wage
                for field in record.payment_method.field_ids:
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
                    elif field.name == 'gosi':
                        salary_amount += record.contract_id.gosi
            record.salary_amount = salary_amount
            remaining_vacation = 0.0
            if record.reconcile_type == 'request':
                remaining_vacation = record.vacation_days
            elif record.reconcile_type == 'balance':
                remaining_vacation = record.balance_days
            elif record.reconcile_type == 'both':
                remaining_vacation = record.balance_days + record.vacation_days
            record.leave_amount = (salary_amount / 30) * remaining_vacation

    @api.multi
    def unlink(self):
        for termination in self:
            if termination.state not in ['draft', 'review']:
                raise Warning(_('You cannot delete a Settlement document'
                                ' which is not draft or cancelled!'))
        return super(Settlement, self).unlink()

    @api.multi
    def open_entries(self):
        context = dict(self._context or {}, search_default_termination_leave_id=self.ids,
                       default_termination_leave_id=self.ids)
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
    _name = "termination.leave.payments"

    name = fields.Char('Name', required=True, help='Payment name')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    ticket_debit_account_id = fields.Many2one('account.account', 'Ticket Debit Account', required=False,
                                              help='Ticket Debit account for journal entry')
    ticket_credit_account_id = fields.Many2one('account.account', 'Ticket Credit Account', required=False,
                                               help='Ticket Credit account for journal entry')
    leave_debit_account_id = fields.Many2one('account.account', 'Leave Debit Account', required=False,
                                             help='Leave Debit account for journal entry')
    leave_credit_account_id = fields.Many2one('account.account', 'Leave Credit Account', required=False,
                                              help='Leave Credit account for journal entry')
    leave_allocate_id = fields.Many2one(comodel_name="hr.leave.allocation", string="Allocation", required=False, )
    field_ids = fields.Many2many(comodel_name="ir.model.fields", relation="leave_field_rel", string="Leave Rules",
                                 domain=[('model_id', '=', 'hr.contract'), ('ttype', 'in', ['float', 'monetary'])])
