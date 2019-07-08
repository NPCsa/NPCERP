# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning


#
class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    @api.model
    def create(self, values):
        res = super(HrPayslip, self).create(values)
        if res.date_from and res.employee_id.return_work and res.date_to:
            if ( res.date_from <= res.employee_id.return_work <= res.date_to or res.date_from > res.employee_id.return_work < res.date_to) and res.employee_id.on_vacation:
                raise Warning(_('You Can not Create Payslip , This Employee %s On Vacation') % (res.employee_id.name))
        return res

    @api.multi
    def write(self, values):
        res = super(HrPayslip, self).write(values)
        if self.date_from and self.employee_id.return_work and self.date_to:
            if (self.date_from <= self.employee_id.return_work <= self.date_to or self.date_from > self.employee_id.return_work < self.date_to) and self.employee_id.on_vacation:
                raise Warning(_('You Can not Create Payslip , This Employee %s On Vacation') % (self.employee_id.name))

        return res
