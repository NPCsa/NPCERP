from odoo import models, fields,api
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_invoice_type(self):
        if self._context:
            active_id = self._context.get('active_id')
            if active_id:
                invoice = self.env['account.invoice'].search([('id','=',active_id)])
                return invoice.type
        return False
    bank_commission = fields.Monetary('Bank Commission')
    commision_tax_id = fields.Many2one('account.tax',string='Vat')
    tax_amount=fields.Monetary('Vat Amount',compute='_compute_amount')
    bank_commission_account=fields.Many2one('account.account',string='Bank Commission Account')
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Vendor Credit Note')],default=default_invoice_type)
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')

    @api.depends('bank_commission', 'commision_tax_id')
    def _compute_amount(self):
        """
        Compute the amounts.
        """
        for line in self:
            # price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.commision_tax_id.compute_all(line.bank_commission, line.currency_id, 1,
                                             product=False, partner=False)
            if taxes:
                if taxes.get('taxes'):
                    line.update({
                        'tax_amount': taxes['taxes'][0]['amount'],
                    })

    @api.multi
    def post(self):
        for rec in self:
            if rec.bank_commission and not rec.payment_type=='transfer':
                if rec.journal_id.default_credit_account_id.user_type_id.name == 'Expenses' or rec.journal_id.default_credit_account_id.user_type_id.name == 'Cost of Revenue':
                    analytic_account = rec.analytic_account_id.id
                else:
                    analytic_account = False

                if rec.bank_commission_account.user_type_id.name == 'Expenses' or rec.bank_commission_account.user_type_id.name == 'Cost of Revenue':
                    analytic_account_1 = rec.analytic_account_id.id
                else:
                    analytic_account_1 = False
                move_commision = self.env['account.move'].create({
                    'name': '/',
                    'journal_id': rec.journal_id.id,
                    'date': rec.payment_date,
                    'line_ids': [(0, 0, {
                        'name': 'Bank Commission',
                        'credit': rec.bank_commission,
                        'analytic_account_id':analytic_account,
                        'account_id': rec.journal_id.default_credit_account_id.id,
                        'payment_id':rec.id
                    }),(0, 0, {
                        'name': 'Bank Commission',
                        'debit': rec.bank_commission,
                        'analytic_account_id':analytic_account_1,
                        'account_id': rec.bank_commission_account.id,
                        'payment_id': rec.id
                    })]
                    })

                move_commision.post()
                if rec.commision_tax_id and rec.tax_amount:
                    move = self.env['account.move'].create({
                        'name': '/',
                        'journal_id': rec.journal_id.id,
                        'date': rec.payment_date,
                        'line_ids': [(0, 0, {
                            'name': 'Bank Commission Tax',
                            'credit': rec.tax_amount,
                            'tax_exigible':False,
                            'tax_ids':[(6,0,[rec.commision_tax_id.id])],
                            'account_id': rec.journal_id.default_credit_account_id.id,
                            'payment_id': rec.id
                        }), (0, 0, {
                            'name': 'Bank Commission Tax',
                            'debit': rec.tax_amount,
                            'tax_exigible':True,
                            'tax_ids':[(6,0,[rec.commision_tax_id.id])],
                            'account_id': rec.commision_tax_id.account_id.id,
                            'payment_id': rec.id
                        })]
                    })
                    move.post()

            if rec.bank_commission and rec.payment_type=='transfer':
                if rec.journal_id.default_credit_account_id.user_type_id.name == 'Expenses' or rec.journal_id.default_credit_account_id.user_type_id.name == 'Cost of Revenue':
                    analytic_account = rec.analytic_account_id.id
                else:
                    analytic_account = False

                if rec.bank_commission_account.user_type_id.name == 'Expenses' or rec.bank_commission_account.user_type_id.name == 'Cost of Revenue':
                    analytic_account_1 = rec.analytic_account_id.id
                else:
                    analytic_account_1 = False
                move_commision = rec.env['account.move'].create({
                    'name': '/',
                    'journal_id': rec.journal_id.id,
                    'date': rec.payment_date,
                    'line_ids': [(0, 0, {
                        'name': 'Bank Commission',
                        'credit': rec.bank_commission,
                        'analytic_account_id':analytic_account,
                        'account_id': rec.journal_id.default_credit_account_id.id,
                        'payment_id':rec.id
                    }),(0, 0, {
                        'name': 'Bank Commission',
                        'debit': rec.bank_commission,
                        'analytic_account_id':analytic_account_1,
                        'account_id': rec.bank_commission_account.id,
                        'payment_id': rec.id
                    })]
                    })

                move_commision.post()
                if rec.commision_tax_id and rec.tax_amount:
                    move = rec.env['account.move'].create({
                        'name': '/',
                        'journal_id': rec.journal_id.id,
                        'date': rec.payment_date,
                        'line_ids': [(0, 0, {
                            'name': 'Bank Commission Tax',
                            'credit': rec.tax_amount,
                            'account_id': rec.journal_id.default_credit_account_id.id,
                            'payment_id': rec.id
                        }), (0, 0, {
                            'name': 'Bank Commission Tax',
                            'debit': rec.tax_amount,
                            'account_id': rec.commision_tax_id.account_id.id,
                            'payment_id': rec.id
                        })]
                    })
                    move.post()
        return super(AccountPayment, self).post()



