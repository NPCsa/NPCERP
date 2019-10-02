# -*- coding: utf-8 -*-

from odoo import models, fields, api

class NewModule(models.Model):
    _inherit = 'hr.termination'

    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related="employee_id.department_id", readonly=True)
    idara_id = fields.Many2one(comodel_name="hr.idara", string="Location", related="employee_id.zw_idara",
                               readonly=True)

class Holiday(models.Model):
    _inherit = 'hr.holiday.termination'

    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related="employee_id.department_id", readonly=True)
    idara_id = fields.Many2one(comodel_name="hr.idara", string="Location", related="employee_id.zw_idara",
                               readonly=True)
