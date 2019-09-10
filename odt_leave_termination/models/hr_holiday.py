# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrHolidays(models.Model):
    _inherit = 'hr.leave.allocation'

    _sql_constraints = [
        ('type_value',
         "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or "
         "(holiday_type='category' AND category_id IS NOT NULL) or "
         "(holiday_type='department' AND department_id IS NOT NULL) or "
         "(holiday_type='company' AND mode_company_id IS NOT NULL))",
         "The employee, department, company or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('duration_check', "CHECK ( number_of_days != 0 )", "The number of days must be greater than 0."),
        ('number_per_interval_check', "CHECK(number_per_interval > 0)", "The number per interval should be greater than 0"),
        ('interval_number_check', "CHECK(interval_number > 0)", "The interval number should be greater than 0"),
    ]

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
                if leave_type and record.holiday_status_id.id in leave_type.ids:
                    record.employee_id.write(
                        {
                         'leave_temp_date_from': record.employee_id.last_allocation_date,
                         'leave_temp_date_to': record.date_from,
                         })
                    record.employee_id.write(
                        {
                            'leave_id': record.id,
                            'last_allocation_date': record.date_to,
                        })
        return res
