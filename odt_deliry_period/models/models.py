# -*- coding: utf-8 -*-

from odoo import models, fields

class DelieryPeriod(models.Model):
	_name = 'deliery.period'

	name = fields.Char(string='Name', required=True)
	period_day = fields.Float(string="Number of days in period",  required=False, )


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    deliery_period = fields.Many2one(comodel_name="deliery.period", string="Deliery Period", required=False, )