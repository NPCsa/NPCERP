# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, models ,fields


class HrHolidaysReport(models.AbstractModel):
    _name = 'report.odootec_hr_holiday.hr_holiday_report'

    def _get_header_info(self, start_date ,end_date):
        st_date = fields.Date.from_string(start_date)
        en_date = fields.Date.from_string(end_date)
        return {
            'start_date': fields.Date.to_string(st_date),
            'end_date': fields.Date.to_string(en_date)
        }

    def _get_data(self, data):
        self.from_date = data['start_date']
        self.to_date = data['end_date']
        self.employee_ids = data['employee_ids']
        employee_obj = self.env['hr.employee'].search([('id','in',self.employee_ids)])
        res = {'data': []}
        for employee in employee_obj:
            data_item =[]
            data_item.append(employee.name)
            initial_balance = self.get_initial_balance(employee)
            data_item.append(initial_balance)
            deduction = self.get_deduction(employee)
            data_item.append(deduction)
            data_item.append(initial_balance - deduction)
            res['data'].append(data_item)
        return res['data']

    def get_initial_balance(self, employee_id):
        holiday_request = self.env['hr.leave']
        holiday_allocate = self.env['hr.leave.allocation']
        holiday_allocation_ids = holiday_allocate.search([('employee_id', '=', employee_id.id),
                                                                        ('state', '=', 'validate')])
        initial_balance = 0
        if holiday_allocation_ids:
            for id in holiday_allocation_ids:
                holiday_rec = holiday_allocate.search([('id', '=', id.id)])
                if not holiday_rec.holiday_status_id.limit:
                    initial_balance += holiday_rec.number_of_days
                initial_balance += holiday_rec.number_of_days
        holiday_request_ids = holiday_request.search([('employee_id', '=', employee_id.id),
                                                                     ('date_to', '<', self.from_date),
                                                                     ('state', '=', 'validate')])
        if holiday_request_ids:
            for id in holiday_request_ids:
                holiday_rec = holiday_request.search([('id', '=', id.id)])
                if not holiday_rec.holiday_status_id.limit:
                    initial_balance += holiday_rec.number_of_days
        return initial_balance

    def get_deduction(self, employee_id):
        holiday_obj = self.env['hr.leave']
        holiday_request_ids = holiday_obj.search([('employee_id', '=', employee_id.id),
                                                                     ('date_from', '>=', self.from_date),
                                                                     ('date_from', '<=', self.to_date),
                                                                     ('date_to', '<=', self.to_date),
                                                                     ('date_to', '>=', self.from_date),
                                                                     ('state', '=', 'validate')])

        deduction = 0
        if holiday_request_ids:
            for id in holiday_request_ids:

                holiday_rec = holiday_obj.search([('id', '=', id.id)])
                if not holiday_rec.holiday_status_id.allocation_type == 'no':
                    deduction += holiday_rec.number_of_days
        return -deduction

    @api.model
    def get_report_values(self, docids, data=None):

        holidays = self.env['hr.leave'].browse(self.ids)
        model = self.env.context.get('active_model')
        docargs = {
            'doc_ids': self.ids,
            'doc_model':model,
            'docs': holidays,
            'get_header_info': self._get_header_info(data['form']['start_date'],data['form']['end_date']),
            'get_data': self._get_data(data['form']),
        }
        return docargs
