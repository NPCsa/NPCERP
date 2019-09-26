# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.rrule import rrule, MONTHLY

from odoo import api, models
from odoo.tools.misc import formatLang, DEFAULT_SERVER_DATETIME_FORMAT

class HrPayslipParser(models.AbstractModel):
    _name = 'report.odt_payslip_employee_report.hr_payroll_employee_report'

    def _get_data(self, data):
        from_date = data['form']['date_from']
        to_date = data['form']['date_to']
        employee_ids = data['form']['employee_ids']
        department_ids = data['form']['department_ids']
        location_ids = data['form']['location_ids']
        salary_rules = self.env['hr.salary.rule'].search([]).ids
        data_final = []
        payslip_obj = self.env['hr.payslip']
        employee_obj = self.env['hr.employee']
        payslip_line_obj = self.env['hr.payslip.line']
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
            employees_loc = [emp.id for department in location_ids for emp in
                         self.env['hr.employee'].search([('zw_idara', '=', department)])]
            employee_data += employees_loc
            employee_data = list(set(employee_data))

        employees = employee_obj.browse(employee_data)

        if employees:
            for employee in employees:
                data = []
                payslip_ids = payslip_obj.search([('employee_id', '=', employee.id),
                                                  ('date_from', '<=', to_date),
                                                  ('date_from', '>=', from_date),
                                                  ('state', '=', 'done'),
                                                  ('is_refund', '=', False)])

                if not payslip_ids:
                    continue
                data.append({'employee':employee})
                all_data = []
                tot_basic = 0.0
                tot_housing = 0.0
                tot_other = 0.0
                tot_net = 0.0
                tot_ded = 0.0
                for payslip in payslip_ids:
                    net = 0.0
                    basic = 0.0
                    housing = 0.0
                    total = 0.0
                    payslip_lines_ids = payslip_line_obj.search([('slip_id', '=', payslip.id)])
                    if not payslip_lines_ids:
                        continue
                    for payslip_line_rec in payslip_lines_ids:
                        if payslip_line_rec.salary_rule_id.id in salary_rules:
                            if payslip_line_rec.salary_rule_id.code == 'BASIC':
                                basic = payslip_line_rec.total
                            elif payslip_line_rec.salary_rule_id.code == 'HA':
                                housing = payslip_line_rec.total
                            elif payslip_line_rec.salary_rule_id.code == 'NET':
                                net = payslip_line_rec.total
                            elif payslip_line_rec.salary_rule_id.code == 'GROSS':
                                total = payslip_line_rec.total
                    deduction = total - net
                    other = total - basic - housing
                    data_list = [payslip.name,net, basic, housing, other, deduction]
                    all_data.append(data_list)
                    tot_net += net
                    tot_basic += basic
                    tot_housing += housing
                    tot_other += other
                    tot_ded += deduction
                total_list = ['Total', tot_net, tot_basic, tot_housing, tot_other, tot_ded]
                all_data.append(total_list)
                data.append(all_data)
                data_final.append(data)
        return data_final


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        get_data = self._get_data(data)

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

