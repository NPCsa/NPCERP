# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    leave_temp_date_from = fields.Date(string="Date From", required=False, )
    leave_temp_date_to = fields.Date(string="Date To", required=False, )
    leave_days_temp = fields.Float(string="Leave Days",  required=False,compute='get_employee_balance_leave')
    leave_id = fields.Many2one(comodel_name="hr.leave", string="Leave", required=False, )

    @api.one
    def get_employee_balance_leave(self):
        for holiday in self:
            leave_days = 0.0
            if holiday.joining_date and holiday.calculate_type == 'manual':
                today = fields.Datetime.from_string(holiday.leave_temp_date_to)
                join_date = fields.Datetime.from_string(holiday.joining_date)
                last_allocation_date = fields.Datetime.from_string(holiday.leave_temp_date_from)
                if today and last_allocation_date:
                    diff = today.date() - join_date.date()
                    allocation_days = (today.date() - last_allocation_date.date()).days
                    service_period = round((diff.days / 365) * 12, 2)

                    allocation_method = holiday.allocation_method
                    day_allocate_lt = 0.0
                    day_allocate_gt = 0.0
                    day_allocate_eq = 0.0
                    if allocation_method:
                        if allocation_method.type_state == 'two':
                            day_allocate_lt = allocation_method.first_year / (365 - allocation_method.first_year)
                            day_allocate_gt = allocation_method.second_year / (365 - allocation_method.second_year)
                            if allocation_days:
                                if service_period <= 60:
                                    leave_days = allocation_days * day_allocate_lt
                                else:

                                    allocate_days = (last_allocation_date.date() - join_date.date()).days
                                    if allocate_days >= 1825:
                                        leave_days = allocation_days * day_allocate_gt
                                    else:
                                        day_to = 0
                                        for n in range(0, allocation_days + 1):

                                            if allocate_days <= 1825:
                                                allocate_days += 1
                                                day_to += 1
                                            else:

                                                days_gt = allocation_days - day_to
                                                leave_days = (days_gt * day_allocate_gt) + (day_to * day_allocate_lt)
                                                break
                        if allocation_method.type_state == 'all':
                            day_allocate_eq = allocation_method.all_year / (365 - allocation_method.all_year)
                            if allocation_days:
                                leave_days = allocation_days * day_allocate_eq

                    if leave_days:
                        self.leave_days_temp = leave_days
