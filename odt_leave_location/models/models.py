# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, models, fields


class ProjectReport(models.AbstractModel):
    _name = 'report.odt_leave_location.hr_holidays_wiz_report'

    def _get_header_info(self, start_date, end_date):
        st_date = fields.Date.from_string(start_date)
        en_date = fields.Date.from_string(end_date)
        return {
            'start_date': fields.Date.to_string(st_date),
            'end_date': fields.Date.to_string(en_date),
        }

    def _get_data(self, data):
        self.report_option = data['report_option']
        self.start_date = data['start_date']
        self.end_date = data['end_date']
        self.department_ids = data['department_ids']
        self.location_ids = data['location_ids']
        if self.report_option == "all":
            holidays_obj = self.env['hr.leave'].search(
                [('date_from', '>=', self.start_date), ('date_to', '<=', self.end_date)])
        elif self.report_option == "department":
            holidays_obj = self.env['hr.leave'].search(
                [('employee_id.department_id', 'in', self.department_ids),
                 ('date_from', '>=', self.start_date), ('date_to', '<=', self.end_date)])
        elif self.report_option == "location":
            holidays_obj = self.env['hr.leave'].search(
                [('employee_id.zw_idara', 'in', self.location_ids),  ('date_from', '>=', self.start_date),
                 ('date_to', '<=', self.end_date)])
        mydata = []
        increment = 1
        if holidays_obj:
            for holidays in holidays_obj:
                dic_holidays = {}
                dic_holidays['increment'] = str(increment)
                dic_holidays['employee'] = holidays.employee_id.name
                # dic_holidays['work_email'] = holidays.employee_id.work_email
                # dic_holidays['work_phone'] = holidays.employee_id.work_phone
                dic_holidays['job'] = holidays.employee_id.job_id.name
                dic_holidays['name'] = holidays.name
                dic_holidays['holiday_type'] = holidays.holiday_status_id.name
                dic_holidays['date_from'] = holidays.date_from
                dic_holidays['date_to'] = holidays.date_to
                # dic_holidays['zw_idara'] = holidays.zw_idara.name
                dic_holidays['department'] = holidays.department_id.name
                dic_holidays['state'] = holidays.state
                mydata.append(dic_holidays)
                increment += 1
        return mydata

    @api.model
    def _get_report_values(self, docids, data=None):
        print("===========nnnnnnnnnnnnnnnnnnnnnnnn==============")
        report = self.env['ir.actions.report']._get_report_from_name('odt_leave_location.hr_holidays_wiz_report')
        print("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm",report)
        holidays = self.env['hr.leave'].browse(self.ids)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': report.model,
            'docs': holidays,
            'get_header_info': self._get_header_info(data['form']['start_date'], data['form']['end_date']),
            'get_data': self._get_data(data['form']),
        }
        return docargs
