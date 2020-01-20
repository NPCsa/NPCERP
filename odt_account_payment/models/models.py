from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    collection_by = fields.Char(string='Collection by')
