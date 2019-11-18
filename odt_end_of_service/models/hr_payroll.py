# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import Warning

from datetime import datetime, timedelta


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def create(self, values):
        res = super(HrPayslip, self).create(values)
        if res.date_from and res.contract_id and res.contract_id.is_terminated and res.date_to:
            if res.date_from <= res.contract_id.date_end <= res.date_to:
                raise Warning(_('You Can not Create Payslip , This Employee %s Is Terminated') % (res.employee_id.name))
        return res

    @api.multi
    def write(self, values):
        res = super(HrPayslip, self).write(values)
        for record in self:
            if record.date_from and record.contract_id and record.contract_id.is_terminated and record.date_to:
                if record.date_from <= record.contract_id.date_end <= record.date_to:
                    raise Warning(
                        _('You Can not Create Payslip , This Employee %s Is Terminated') % (record.employee_id.name))
        return res