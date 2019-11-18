# -*- coding: utf-8 -*-


from odoo import models, fields, api, _



class HrHolidaysStatus(models.Model):
    _inherit = "hr.leave.type"
    is_depend_eos = fields.Boolean('Is depend End of Service.')
