# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    leave_temp_date_from = fields.Date(string="Date From", required=False, )
    leave_temp_date_to = fields.Date(string="Date To", required=False, )
    leave_days_temp = fields.Float(string="Leave Days",  required=False, )