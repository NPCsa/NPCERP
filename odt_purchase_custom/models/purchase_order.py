from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vendor_invoice_number = fields.Char(string='Vendor Invoice No',required=False)

    _sql_constraints = [
        ('vendor_invoice_number_uniq',
         'UNIQUE (vendor_invoice_number)',
         'The Vendor Invoice No must be unique!')]