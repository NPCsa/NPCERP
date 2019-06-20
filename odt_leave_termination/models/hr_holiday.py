# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrHolidays(models.Model):
    _inherit = 'hr.leave'

    @api.multi
    def action_validate(self):
        res = super(HrHolidays, self).action_validate()
        data_holiday = self.browse(self._ids)
        for record in data_holiday:
            if record.date_to != False:
                leave_type = self.env['hr.leave.type']
                if record.employee_id.holiday_line_ids:
                    leave_type = record.employee_id.holiday_line_ids.mapped('leave_status_id')
                elif record.employee_id.holiday_line_man_ids:
                    leave_type = record.employee_id.holiday_line_man_ids.mapped('leave_status_id')
                print('------leave_type----------',leave_type)
                print('------holiday_status_id----------',record.holiday_status_id)
                print('------date_from----------',record.date_from)
                print('------date_to----------',record.date_to)
                if leave_type and record.holiday_status_id.id in leave_type.ids:
                    record.employee_id.write(
                        {'leave_temp_date_from': record.date_from, 'leave_temp_date_to': record.date_to,
                         'leave_days_temp': record.number_of_days})
        return res
