# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.rrule import rrule, MONTHLY

from odoo import api, models
from odoo.tools.misc import formatLang, DEFAULT_SERVER_DATETIME_FORMAT


class HrContractParser(models.AbstractModel):
    _name = 'report.odt_contracts_reports.hr_contracts_employee_report'

    def _get_data(self, data):
        from_date = data['form']['date_from']
        to_date = data['form']['date_to']
        state = data['form']['state']
        filter_by = data['form']['filter_by']
        employee_ids = data['form']['employee_ids']
        department_ids = data['form']['department_ids']
        # location_ids = data['form']['location_ids']
        data_final = []
        contracts_obj = self.env['hr.contract']
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
        # if location_ids:
        #     employees_loc = [emp.id for location in location_ids for emp in
        #                      self.env['hr.employee'].search([('zw_idara', '=', location)])]
        #     employee_data += employees_loc
            employee_data = list(set(employee_data))
        if employee_data:
            employees = employee_obj.browse(employee_data)
        else:
            employees = employee_obj.search([])

        if employees:
            if filter_by == 'depart':
                departments = employees.mapped('department_id')
                for department in departments:
                    data_dep = []
                    employees_ids = employees.filtered(lambda emp: emp.department_id.id == department.id)
                    if employees_ids:
                        data = [department.name]
                        data_dep.append(data)
                        for employee in employees_ids:
                            if state == 'all':
                                contracts_ids = contracts_obj.search([('employee_id', '=', employee.id),
                                                                      ('date_start', '<=', to_date),
                                                                      ('date_start', '>=', from_date), ])
                            else:
                                contracts_ids = contracts_obj.search([('employee_id', '=', employee.id),
                                                                      ('date_start', '<=', to_date),
                                                                      ('date_start', '>=', from_date),
                                                                      ('state', '=', state), ])
                            if not contracts_ids:
                                continue
                            for contract in contracts_ids:
                                line = [contract.employee_id.name, contract.name,
                                        contract.state, contract.date_start, contract.date_end,
                                        contract.job_id.name, contract.department_id.name,
                                        contract.wage,contract.transportation_allowance,
                                        contract.housing_allowance, contract.mobile_allowance, contract.other_allowance,
                                        contract.deduction,
                                        contract.gosi, contract.total_salary, contract.notes]
                                data_dep.append(line)
                        data_final.append(data_dep)
            # elif filter_by == 'location':
            #     departments = employees.mapped('zw_idara')
            #     for department in departments:
            #         data_dep = []
            #         employees_ids = employees.filtered(lambda emp: emp.zw_idara.id == department.id)
            #         if employees_ids:
            #             data = [department.name]
            #             data_dep.append(data)
            #             for employee in employees_ids:
            #                 if state == 'all':
            #                     contracts_ids = contracts_obj.search([('employee_id', '=', employee.id),
            #                                                           ('date_start', '<=', to_date),
            #                                                           ('date_start', '>=', from_date), ])
            #                 else:
            #                     contracts_ids = contracts_obj.search([('employee_id', '=', employee.id),
            #                                                           ('date_start', '<=', to_date),
            #                                                           ('date_start', '>=', from_date),
            #                                                           ('state', '=', state), ])
            #                 if not contracts_ids:
            #                     continue
            #                 for contract in contracts_ids:
            #                     line = [contract.employee_id.name, contract.employee_id.employee_id, contract.name,
            #                             contract.state, contract.date_start, contract.date_end,
            #                             contract.job_id.name, contract.zw_idara.name, contract.department_id.name,
            #                             contract.wage,
            #                             contract.gosi, contract.total_salary, contract.notes]
            #                     data_dep.append(line)
            #             data_final.append(data_dep)
            elif filter_by == 'employee':
                for employee in employees:
                    data_dep = []
                    if state == 'all':
                        contracts_ids = contracts_obj.search([('employee_id', '=', employee.id),
                                                              ('date_start', '<=', to_date),
                                                              ('date_start', '>=', from_date), ])
                    else:
                        contracts_ids = contracts_obj.search([('employee_id', '=', employee.id),
                                                              ('date_start', '<=', to_date),
                                                              ('date_start', '>=', from_date),
                                                              ('state', '=', state), ])
                    if not contracts_ids:
                        continue
                    for contract in contracts_ids:
                        line = [contract.employee_id.name, contract.name,
                                contract.state, contract.date_start, contract.date_end,
                                contract.job_id.name, contract.department_id.name,
                                contract.wage, contract.transportation_allowance,
                                contract.housing_allowance, contract.mobile_allowance, contract.other_allowance,
                                contract.deduction,
                                contract.gosi, contract.total_salary, contract.notes]
                        data_dep.append(line)
                    data_final.append(data_dep)
        return data_final

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        state = data['form']['state']
        filter_by = data['form']['filter_by']
        if filter_by == 'depart':
            filter_by = 'Department'
        # elif filter_by == 'location':
        #     filter_by = 'Location'
        elif filter_by == 'employee':
            filter_by = 'Employee'
        if state == 'draft':
            state = 'New'
        elif state == 'open':
            state = 'Running'
        elif state == 'pending':
            state = 'To Renew'
        elif state == 'close':
            state = 'Expired'
        elif state == 'cancel':
            state = 'Cancelled'
        elif state == 'all':
            state = 'All'
        get_data = self._get_data(data)
        return {
            'doc_ids': docids,
            'get_data': get_data,
            'doc_model': model,
            'date_from': date_from,
            'date_to': date_to,
            'state': state,
            'filter_by': filter_by,
            'data': data,
            'docs': docs,
            'formatLang': formatLang
        }
