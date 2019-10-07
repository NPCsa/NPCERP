# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import Warning


class AccountMove(models.Model):
    _inherit = 'account.move'

    termination_leave_id = fields.Many2one('hr.holiday.termination', 'Settlement', help='Settlement Record')


class Termination(models.Model):
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
    contract_id = fields.Many2one('hr.contract', 'Contract', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    job_id = fields.Many2one('hr.job', 'Job Title', readonly=True, states={'draft': [('readonly', False)]})
    leave_date = fields.Date('leave Date From', required=True, readonly=True,
                             states={'draft': [('readonly', False)]}, defualt=fields.Date.today())
    last_leave_date = fields.Date('leave Date To', readonly=True, required=True,
                                  states={'draft': [('readonly', False)]})
    approved_by = fields.Many2one('res.users', 'Approved By', default=lambda self: self.env.user, readonly=True,
                                  states={'draft': [('readonly', False)]})
    approval_date = fields.Date('Approval Date', readonly=True, states={'draft': [('readonly', False)]})
    vacation_days = fields.Float('Vacation Days', readonly=True, states={'draft': [('readonly', False)]})
    salary_amount = fields.Float('Salary Amount', readonly=True, states={'draft': [('readonly', False)]})
    leave_amount = fields.Float(string="Leave Amount", required=False,
                                help="Calculation By (Total Salary - Transportation Allowance) / 30 ")
    ticket_amount = fields.Float(string="Ticket Amount", required=False, )
    total_amount = fields.Float(string="Total Amount", required=False, compute='_compute_total_amount')
    move_id = fields.Many2one('account.move', 'Journal Entry', help='Journal Entry for Termination')

    payment_method = fields.Many2one('termination.leave.payments', 'Payment Method',
                                     help='payment method for Settlement')
    journal_id = fields.Many2one('account.journal', 'Journal', help='Journal for journal entry')
    notes = fields.Text(string="Notes", required=False, )
    state = fields.Selection([('draft', _('Draft')),
                              ('review', _('Review')),
                              ('approved', _('First Approve')),
                              ('approved2', _('Second Approve'))
                              ], _('Status'), readonly=True, copy=False, default='draft',
                             help=_("Gives the status of the Settlement"), select=True)



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

    @api.multi
    def validate_termination(self):
        if self.employee_id.allocation_method:
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

            if not self.employee_id.allocation_method:
                raise Warning(_('Please Set Allocation method'))

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
            move_id.post()
        return True

    @api.multi
    def get_contracts(self):
        contract_obj = self.env['hr.contract']
        contract_ids = []
        for termination in self:
            date_to = termination.leave_date
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

    # @api.multi
    # def get_employee_balance_leave(self):
    #     for holiday in self:
    #         leave_days = 0.0
    #         if holiday.employee_id.joining_date and holiday.leave_date and holiday.last_leave_date and holiday.employee_id.calculate_type == 'manual':
    #             today = fields.Datetime.from_string(holiday.leave_date)
    #             join_date = fields.Datetime.from_string(holiday.employee_id.joining_date)
    #             last_leave_date = fields.Datetime.from_string(holiday.last_leave_date)
    #             diff = today.date() - join_date.date()
    #             allocation_days = (today.date() - last_leave_date.date()).days
    #             service_period = round((diff.days / 365) * 12, 2)
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
    #                             allocate_days = (last_leave_date.date() - join_date.date()).days
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
    #         return leave_days

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.contract_id = False
        if self.employee_id:
            vals = {'domain': {'contract_id': False}}
            self.job_id = self.employee_id.job_id.id
            self.leave_date = self.employee_id.leave_temp_date_from
            self.last_leave_date = self.employee_id.leave_temp_date_to
            remaining_vacation = self.employee_id.leave_days_temp
            self.vacation_days = remaining_vacation
            contracts = self.get_contracts()
            if contracts:
                return {'domain': {'contract_id': [('id', 'in', contracts.ids)]}}
            return vals

    @api.onchange('contract_id', 'employee_id','payment_method')
    def _onchange_contract_id(self):
        for record in self:
            salary_amount = 0.0
            if record.contract_id and record.payment_method:
                basic = record.contract_id.wage
                for field in record.payment_method.field_ids:
                    if field.name == 'wage':
                        salary_amount += record.contract_id[field.name]
                    elif field.name == 'transportation_allowance':
                        salary_amount += (basic * (record.contract_id.transportation_allowance / 100) if record.contract_id.is_trans else record.contract_id.transportation_allowance)
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

            record.salary_amount = salary_amount
            remaining_vacation = record.employee_id.leave_days_temp
            record.vacation_days = remaining_vacation
            record.leave_amount = (salary_amount / 30) * remaining_vacation

    @api.multi
    def unlink(self):
        for termination in self:
            if termination.state not in ['draft', 'review']:
                raise Warning(_('You cannot delete a Settlement document'
                                ' which is not draft or cancelled!'))
        return super(Termination, self).unlink()

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
    field_ids = fields.Many2many('ir.model.fields', 'leave_field_rel', 'termination_id', 'field_id', 'Calculation Lines',
                                 domain=[('model_id', '=', 'hr.contract'), ('ttype', 'in', ['float', 'monetary'])])
