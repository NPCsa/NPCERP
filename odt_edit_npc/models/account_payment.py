# -*- coding: utf-8 -*-

from odoo import models, fields, api

class NewModule(models.Model):
    _inherit = 'account.payment'

    bank_check = fields.Char(string="Bank Check Number", required=False, )
    bank_name = fields.Char(string="Bank Name", required=False, )
    date_check = fields.Date(string="Date of The Check", required=False, )
