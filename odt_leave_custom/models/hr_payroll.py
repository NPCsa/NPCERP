# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################


from datetime import date, datetime, time as datetime_time
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from pytz import timezone

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    leave_days = fields.Float(
        string='Previous Leave Days',
    )


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        res = super(Payslip, self).get_worked_day_lines(
            contract_ids, date_from, date_to)
        for contract in contract_ids.filtered(lambda contract: contract.resource_calendar_id):
            date_start_from = fields.Date.to_string(
                (fields.Date.from_string(date_from) + relativedelta(month=1, day=1)))
            date_end_to = fields.Date.to_string(
                (fields.Date.from_string(date_from) + relativedelta(days=-1)))
            day_from = datetime.combine(fields.Date.from_string(
                date_start_from), datetime_time.min)
            day_to = datetime.combine(
                fields.Date.from_string(date_end_to), datetime_time.max)
            # compute leave days
            leaves = {}
            calendar = contract.resource_calendar_id
            tz = timezone(calendar.tz)
            day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to,
                                                                   calendar=contract.resource_calendar_id)
            for day, hours, leave in day_leave_intervals:
                holiday = leave.holiday_id
                current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                    'name': holiday.holiday_status_id.name,
                    'leave_code': holiday.holiday_status_id.code,
                    'number_of_days': 0.0,
                })
                work_hours = calendar.get_work_hours_count(
                    tz.localize(datetime.combine(day, datetime_time.min)),
                    tz.localize(datetime.combine(day, datetime_time.max)),
                    compute_leaves=False,
                )
                if work_hours:
                    current_leave_struct['number_of_days'] += hours / work_hours

            for rule in res:
                if rule['code']:
                    code = rule['code']
                    leave = self.env['hr.leave.type'].sudo().search(
                        [('name', '=', code)])
                    if leave:
                        rule['code'] = leave.code
                        if leaves:
                            for element in leaves:
                                leave_id = leaves[element]
                                if code == leave_id['name']:
                                    rule['leave_days'] = leave_id['number_of_days']

        return res


# previous_leave_days = worked_days.Sick and worked_days.Sick.leave_days
# current_leave_days = worked_days.Sick and worked_days.Sick.number_of_days
# leave_days = previous_leave_days+current_leave_days
# if previous_leave_days:
#     if leave_days <= 30:
#         result = 0.0
#     elif leave_days <= 90:
#         if previous_leave_days <= 30:
#             first_leave_days = 30-previous_leave_days
#             second_leave_days = leave_days-previous_leave_days
#             final_leave_days = second_leave_days-first_leave_days
#             result = final_leave_days*0.25
#         else:
#             result = current_leave_days*0.25
#     else:
#         if previous_leave_days <= 90:
#             first_leave_days = 90-previous_leave_days
#             first_leave_amount = first_leave_days*0.25
#             second_leave_days = leave_days-previous_leave_days
#             final_leave_days = second_leave_days-first_leave_days
#             result = final_leave_days + first_leave_amount
#         else:
#             result = current_leave_days
# else:
#     if current_leave_days > 30:
#         result = 30-current_leave_days
#     else:
#         result = 0.0
