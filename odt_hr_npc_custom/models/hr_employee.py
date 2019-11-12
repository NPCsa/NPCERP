# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    payment_method = fields.Selection(string="Payment Method",
                                      selection=[('cash', 'Cash'), ('bank', 'Bank'),('other', 'Other'), ], required=False, default='cash')

    # @api.model
    # def create(self, values):
    #     res = super(HrEmployee, self).create(values)
    #     name = self.get_original_name(values.get('first_name', res.first_name),
    #                                   values.get('second_name', res.second_name),
    #                                   values.get('third_name', res.third_name),
    #                                   values.get('last_name', res.last_name))
    #     partner = self.env['res.partner'].sudo().create({'name': str(name), 'customer': False, 'employee': True})
    #     res.address_home_id = partner.id
    #     return res
    #
    # @api.multi
    # def write(self, vals):
    #     res = super(HrEmployee, self).write(vals)
    #     for record in self:
    #         name = self.get_original_name(vals.get('first_name', record.first_name),
    #                                       vals.get('second_name', record.second_name),
    #                                       vals.get('third_name', record.third_name),
    #                                       vals.get('last_name', record.last_name))
    #         record.address_home_id.update({'name': str(name)})
    #     return res