# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    payment_method = fields.Selection(string="Payment Method",
                                      selection=[('cash', 'Cash'), ('bank', 'Bank'),('other', 'Other'), ], required=False, default='cash')

