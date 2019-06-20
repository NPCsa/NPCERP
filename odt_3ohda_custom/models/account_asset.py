# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    model = fields.Char(string="Code", required=False, )
    notes = fields.Text(string="description", required=False, )

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search(['|','|',('name', operator, name), ('model', operator, name), ('notes', operator, name)] + args, limit=limit)
        if not recs.ids:
            return super(AccountAssetAsset, self).name_search(name=name, args=args,
                                                              operator=operator,
                                                              limit=limit)
        return recs.name_get()
