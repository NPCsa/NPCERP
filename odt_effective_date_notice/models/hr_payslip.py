# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import Warning


#
class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def create(self, values):
        res = super(HrPayslip, self).create(values)
        if res.date_from and res.date_to:
            clause_1 = ['&', ('date_to', '<=', res.date_to), ('date_to', '>=', res.date_from)]
            # OR if it starts between the given dates
            clause_2 = ['&', ('date_from', '<=', res.date_to), ('date_from', '>=', res.date_from)]
            # OR if it starts before the date_from and finish after the date_end (or never finish)
            clause_3 = ['&', ('date_from', '<=', res.date_from), ('date_from', '>=', res.date_to)]

            clause_final = [('state', 'in', ['validate', 'validate1']),
                            ('employee_id', '=', res.employee_id.id), '|',
                            '|'] + clause_1 + clause_2 + clause_3
            request_leaves = self.env['hr.leave'].sudo().search(clause_final)
            
            if any(res.date_from <= datetime.strptime(str(leave.date_to)[:10], "%Y-%m-%d").date() <= res.date_to and (
                    not leave.effective_id or leave.effective_id.state != 'confirm') for leave in
                   request_leaves) and res.employee_id.on_vacation:
                raise Warning(_('You Can not Create Payslip , This Employee %s On Vacation') % (res.employee_id.name))
            elif not request_leaves and res.employee_id.on_vacation and res.employee_id.return_work <= res.date_from:
                raise Warning(_('You Can not Create Payslip , This Employee %s On Vacation') % (res.employee_id.name))
        return res

    @api.multi
    def write(self, values):
        res = super(HrPayslip, self).write(values)
        if self.date_from and self.date_to:
            clause_1 = ['&', ('date_to', '<=', self.date_to), ('date_to', '>=', self.date_from)]
            # OR if it starts between the given dates
            clause_2 = ['&', ('date_from', '<=', self.date_to), ('date_from', '>=', self.date_from)]
            # OR if it starts before the date_from and finish after the date_end (or never finish)
            clause_3 = ['&', ('date_from', '<=', self.date_from), ('date_from', '>=', self.date_to)]

            clause_final = [('state', 'in', ['validate', 'validate1']),
                            ('employee_id', '=', self.employee_id.id), '|',
                            '|'] + clause_1 + clause_2 + clause_3
            request_leaves = self.env['hr.leave'].sudo().search(clause_final)

            if any(self.date_from <= datetime.strptime(str(leave.date_to)[:10], "%Y-%m-%d").date() <= self.date_to and (
                    not leave.effective_id or leave.effective_id.state != 'confirm') for leave in
                   request_leaves) and self.employee_id.on_vacation:
                raise Warning(_('You Can not Create Payslip , This Employee %s On Vacation') % (self.employee_id.name))
            elif not request_leaves and self.employee_id.on_vacation and self.employee_id.return_work <= self.date_from:
                raise Warning(_('You Can not Create Payslip , This Employee %s On Vacation') % (self.employee_id.name))
        return res
