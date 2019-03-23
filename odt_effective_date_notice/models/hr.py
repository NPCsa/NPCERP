
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime , timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fixed_overtime = fields.Float(string="Fixed OverTime",  required=False, )
    on_vacation = fields.Boolean(string="On Vacation")
    return_work = fields.Date(string="Return Date", required=False, )
    absent_ids = fields.One2many(comodel_name="hr.effective.date", inverse_name="employee_id", string="Absence", required=False, )


class HrHolidays(models.Model):
    _inherit = 'hr.leave'

    @api.multi
    def action_validate(self):
        data_holiday =  self.browse(self._ids)
        for record in data_holiday:
           if record.date_to != False:
                return_date = datetime.strptime(record.date_to, "%Y-%m-%d %H:%M:%S").date()
                record.employee_id.write({'on_vacation': True, 'return_work': return_date + timedelta(days=+1)})
        return super(HrHolidays, self).action_validate()

