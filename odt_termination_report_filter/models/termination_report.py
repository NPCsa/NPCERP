# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, models, fields


class ProjectReport(models.AbstractModel):
    _name = 'report.odt_termination_report_filter.report_termination_wiz'

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
            termination_obj = self.env['hr.termination'].search(
                [('date', '>=', self.start_date), ('date', '<=', self.end_date)])
        elif self.report_option == "department":
            termination_obj = self.env['hr.termination'].search(
                [('department_id', 'in', self.department_ids),
                 ('date', '>=', self.start_date), ('date', '<=', self.end_date)])
        elif self.report_option == "location":
            termination_obj = self.env['hr.termination'].search(
                [('idara_id', 'in', self.location_ids), ('date', '>=', self.start_date),
                 ('date', '<=', self.end_date)])
        mydata = []
        increment = 1
        if termination_obj:
            for termination in termination_obj:
                dic_termination = {}
                dic_termination['increment'] = str(increment)
                dic_termination['number'] = termination.termination_code
                dic_termination['employee'] = termination.employee_id.name
                dic_termination['employee_code'] = termination.employee_code
                dic_termination['date'] = termination.date
                dic_termination['contract_id'] = termination.contract_id.name
                dic_termination['zw_idara'] = termination.idara_id.name
                dic_termination['department'] = termination.department_id.name
                dic_termination['state'] = termination.state
                dic_termination['total_deserve'] = termination.total_deserve
                dic_termination['deserve_salary_amount'] = termination.deserve_salary_amount
                dic_termination['add_value'] = termination.add_value
                dic_termination['ded_value'] = termination.ded_value
                dic_termination['loan_value'] = termination.loan_value
                dic_termination['total_deserve_amount'] = termination.total_deserve_amount
                mydata.append(dic_termination)
                increment += 1
        return mydata

    @api.model
    def _get_report_values(self, docids, data=None):
        print("--------------------------------")
        report = self.env['ir.actions.report']._get_report_from_name('odt_termination_report_filter.report_termination_wiz')
        termination = self.env['hr.termination'].browse(self.ids)
        return {
            'doc_ids': self.ids,
            'doc_model': report.model,
            'docs': termination,
            'get_header_info': self._get_header_info(data['form']['start_date'], data['form']['end_date']),
            'get_data': self._get_data(data['form']),
        }
