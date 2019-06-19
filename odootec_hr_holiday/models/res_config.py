# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID, _


class addsol_hr_attendance_payroll_config_settings(models.TransientModel):
    _inherit = 'hr.config.settings'

    allocation_range = fields.Selection([('month', 'Month'), ('year', 'Year')],
                                        'Allocate automatic leaves every', required=True,
                                        help="Periodicity on which you want automatic allocation of leaves to eligible employees.")

    def get_default_allocation(self, cr, uid, fields, context=None):
        ir_values = self.pool.get('ir.values')
        allocation_range = ir_values.get_default(cr, uid, 'hr.config.settings', 'allocation_range')
        return {
            'allocation_range': allocation_range,
        }

    def set_default_allocation(self, cr, uid, ids, context=None):
        ir_values = self.pool.get('ir.values')
        wizard = self.browse(cr, uid, ids)[0]
        if wizard.allocation_range:
            allocation_range = wizard.allocation_range
        else:
            allocation_range = False
        ir_values.set_default(cr, SUPERUSER_ID, 'hr.config.settings', 'allocation_range', allocation_range)

