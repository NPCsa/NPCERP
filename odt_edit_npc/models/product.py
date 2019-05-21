# -*- coding: utf-8 -*-

from odoo import models, fields, api

class NewModule(models.Model):
    _name = "product.category"
    _inherit = ['product.category','mail.thread']

    name = fields.Char('Name', index=True, required=True, translate=True,track_visibility='onchange')
    parent_id = fields.Many2one('product.category', 'Parent Category', index=True, ondelete='cascade',track_visibility='onchange')
    child_id = fields.One2many('product.category', 'parent_id', 'Child Categories',track_visibility='onchange')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False,track_visibility='onchange' )

class NewModule_product(models.Model):
    _inherit = 'product.template'

    def _get_default_category_id(self):
        return self.env["product.category"].search([('company_id','=',self.env.user.company_id.id)], limit=1, order='id').id

    categ_id = fields.Many2one(
        'product.category', 'Product Category',
        change_default=True, default=_get_default_category_id,
        required=True, help="Select category for the current product")
