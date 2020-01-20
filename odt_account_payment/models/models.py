from odoo import api, fields, models,_
from odoo.exceptions import AccessError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    collection_by = fields.Char(string='Collection by')

    @api.multi
    def post(self):
        if not self.env.user.has_group('odt_account_payment.group_account_payment_confirm'):
            raise AccessError(_("Do not have access, for confirm payment"))
        return super(AccountPayment, self).post()
        

