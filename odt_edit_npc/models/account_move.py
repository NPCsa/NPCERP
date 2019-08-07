# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['mail.thread', 'account.move']
    _description = "Journal Entries"
    _order = 'date desc, id desc'

    @api.multi
    def _get_default_journal(self):
        if self.env.context.get('default_journal_type'):
            return self.env['account.journal'].search([('company_id', '=', self.env.user.company_id.id),
                                                       ('type', '=', self.env.context['default_journal_type'])],
                                                      limit=1).id

    name = fields.Char(string='Number', required=True, copy=False, default='/',track_visibility='onchange')
    ref = fields.Char(string='Reference', copy=False)
    date = fields.Date(required=True, states={'posted': [('readonly', True)]}, index=True,
                       default=fields.Date.context_today,track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                 states={'posted': [('readonly', True)]}, default=_get_default_journal,track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=True, string="Currency",track_visibility='onchange')
    state = fields.Selection([('draft', 'Unposted'), ('posted', 'Posted')], string='Status',track_visibility='onchange',
                             required=True, readonly=True, copy=False, default='draft',
                             help='All manually created new journal entries are usually in the status \'Unposted\', '
                                  'but you can set the option to skip that status on the related journal. '
                                  'In that case, they will behave as journal entries automatically created by the '
                                  'system on document validation (invoices, bank statements...) and will be created '
                                  'in \'Posted\' status.')
    line_ids = fields.One2many('account.move.line', 'move_id', string='Journal Items',track_visibility='onchange',
                               states={'posted': [('readonly', True)]}, copy=True)
    partner_id = fields.Many2one('res.partner', compute='_compute_partner_id', string="Partner", store=True,track_visibility='onchange',
                                 readonly=True)
    amount = fields.Monetary(compute='_amount_compute', store=True,track_visibility='onchange')
    narration = fields.Text(string='Internal Note',track_visibility='onchange')
    company_id = fields.Many2one('res.company', related='journal_id.company_id',track_visibility='onchange', string='Company', store=True,
                                 readonly=True)
    matched_percentage = fields.Float('Percentage Matched', compute='_compute_matched_percentage', digits=0,track_visibility='onchange', store=True,
                                      readonly=True, help="Technical field used in cash basis method")
    # Dummy Account field to search on account.move by account_id
    dummy_account_id = fields.Many2one('account.account', related='line_ids.account_id', string='Account', store=False,track_visibility='onchange',
                                       readonly=True)
    tax_cash_basis_rec_id = fields.Many2one(
        'account.partial.reconcile',track_visibility='onchange',
        string='Tax Cash Basis Entry of',
        help="Technical field used to keep track of the tax cash basis reconciliation. "
             "This is needed when cancelling the source: it will post the inverse journal entry to cancel that part too.")
    auto_reverse = fields.Boolean(string='Reverse Automatically',track_visibility='onchange', default=False,
                                  help='If this checkbox is ticked, this entry will be automatically reversed at the reversal date you defined.')
    reverse_date = fields.Date(string='Reversal Date', help='Date of the reverse accounting entry.',track_visibility='onchange')
    reverse_entry_id = fields.Many2one('account.move', String="Reverse entry", store=True, readonly=True,track_visibility='onchange')
    tax_type_domain = fields.Char(store=False,track_visibility='onchange',
                                  help='Technical field used to have a dynamic taxes domain on the form view.')

class NewModule(models.Model):
    _inherit = 'account.move.line'

    parent_account = fields.Many2one(comodel_name="account.account", string="Group of Account", required=False, )

class Account(models.Model):
    _inherit = 'account.account'

    is_default_receivable = fields.Boolean()
    is_default_payable = fields.Boolean()

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange('company_id')
    def _get_accounts(self):
        account_receivable_obj = self.env['account.account'].search([('company_id','=',self.company_id.id),('is_default_receivable','=',True)])
        account_payable_obj = self.env['account.account'].search([('company_id','=',self.company_id.id),('is_default_payable','=',True)])
        if account_receivable_obj :
            self.property_account_receivable_id = account_receivable_obj[0].id
        if account_payable_obj:
            self.property_account_payable_id = account_payable_obj[0].id