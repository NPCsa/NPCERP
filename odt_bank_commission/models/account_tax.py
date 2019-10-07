from odoo import models, fields,api
from odoo.exceptions import UserError

class AccountTax(models.Model):
    _inherit = "account.tax"

    default_bank_commission = fields.Boolean('Bank Commission Tax')