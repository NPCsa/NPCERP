# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _compute_eos_leaves(self):
        self._cr.execute("""SELECT
                sum(h.number_of_days) as days,
                h.employee_id
            from
                hr_leave h
                join hr_leave_type s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                s.is_depend_eos=True and
                h.employee_id in %s
            group by h.employee_id""", (tuple(self.ids),))

        res = self._cr.dictfetchall()
        for re in res:
            self.browse(re['employee_id']).total_eos_leaves = -re['days']

    total_eos_leaves = fields.Float('No of Leaves Depend EOS', compute='_compute_eos_leaves')