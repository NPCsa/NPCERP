# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.rrule import rrule, MONTHLY

from odoo import api, models
from odoo.tools.misc import formatLang, DEFAULT_SERVER_DATETIME_FORMAT


class HrContractParser(models.AbstractModel):
    _name = 'report.odt_contract_employee_report.hr_contract_employee_report'

    def _get_data(self, data):
        from_date = data['form']['date_from']
        to_date = data['form']['date_to']
        state = data['form']['state']
        employee_ids = data['form']['employee_ids']
        department_ids = data['form']['department_ids']
        location_ids = data['form']['location_ids']
        data_final = []
        contract_obj = self.env['hr.contract']
        employee_obj = self.env['hr.employee']
        employee_data = []
        if employee_ids:
            employee_data += employee_ids
            employee_data = list(set(employee_data))
        if department_ids:
            employees_dep = [emp.id for department in department_ids for emp in
                             self.env['hr.employee'].search([('department_id', '=', department)])]
            employee_data += employees_dep
            employee_data = list(set(employee_data))
        if location_ids:
            employees_loc = [emp.id for location in location_ids for emp in
                             self.env['hr.employee'].search([('zw_idara', '=', location)])]
            employee_data += employees_loc
            employee_data = list(set(employee_data))
        if employee_data:
            employees = employee_obj.browse(employee_data)
        else:
            employees = employee_obj.search([])

        if employees:
            for employee in employees:
                data = []
                if state == 'all':
                    contract_ids = contract_obj.search([('employee_id', '=', employee.id),
                                                        ('date_start', '<=', to_date),
                                                        ('date_start', '>=', from_date), ])
                else:
                    contract_ids = contract_obj.search([('employee_id', '=', employee.id),
                                                        ('date_start', '<=', to_date),
                                                        ('date_start', '>=', from_date),
                                                        ('state', '=', state), ])

                if not contract_ids:
                    continue
                data.append({'employee': employee})
                all_data = []
                for contract in contract_ids:
                    line = [contract.name,contract.state, contract.date_start, contract.date_end,
                              contract.department_id.name, contract.wage, contract.transportation_allowance,
                            contract.housing_allowance,contract.mobile_allowance,contract.other_allowance,contract.deduction,
                            contract.gosi, contract.total_salary, contract.notes]
                    all_data.append(line)
                data.append(all_data)
                data_final.append(data)
                print("++++++++++++++++++++++++++++++++++++",data_final)
        return data_final

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        get_data = self._get_data(data)
        print("=======================================",get_data)
        return {
            'doc_ids': docids,
            'get_data': get_data,
            'doc_model': model,
            'date_from': date_from,
            'date_to': date_to,
            'data': data,
            'docs': docs,
            'formatLang': formatLang
        }
