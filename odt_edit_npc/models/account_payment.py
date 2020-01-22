# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import AccessError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    bank_check = fields.Char(string="Bank Check Number", required=False, )
    bank_name = fields.Char(string="Bank Name", required=False, )
    date_check = fields.Date(string="Date of The Check", required=False, )
    collection_by = fields.Char(string='Collection by')

    @api.multi
    def post(self):
        if not self.env.user.has_group('odt_account_payment.group_account_payment_confirm'):
            raise AccessError(_("Do not have access, for confirm payment"))
        return super(AccountPayment, self).post()
