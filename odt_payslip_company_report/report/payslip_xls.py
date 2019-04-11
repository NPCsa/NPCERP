# -*- coding: utf-8 -*-

from odoo import models


class PayrollXlsx(models.AbstractModel):
    _name = 'report.odt_payslip_company_report.report_payroll_company_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, payslips):

        employees = False
        from_date = ''
        to_date = ''
        for line in payslips:
            employees = line.employee_ids
            salary_rules = line.rule_ids.ids or self.env['hr.salary.rule'].search([]).sorted(
                key=lambda v: v.sequence).ids
            from_date = line.date_from
            to_date = line.date_to
            state = line.state

        payslip_obj = self.env['hr.payslip']
        payslip_line_obj = self.env['hr.payslip.line']

        sheet = workbook.add_worksheet('Hr Payslip Info')
        format1 = workbook.add_format(
            {'font_size': 10, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
             'bold': True})
        format2 = workbook.add_format(
            {'font_size': 10, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
             'bold': True})
        format2.set_align('center')
        format2.set_align('vcenter')
        format2.set_color('white')
        format2.set_bg_color('blue')

        sheet.right_to_left()
        sheet.set_column(0, 18, 20)
        sheet.insert_image('B2', '../static/images/logo.jpeg')

        sheet.merge_range('H7:O7', 'كشف المرتبات', format2)
        sheet.merge_range('H8:I8', 'التاريخ ', format2)
        sheet.merge_range('L10:K10', str('Payslips Status ' + str(state)), format2)
        sheet.merge_range('J8:O8', str(' من  ' + str(from_date) + 'الى  ' + str(to_date)), format2)
        sheet.merge_range('A12:A13', 'الادارة', format2)
        sheet.merge_range('B12:B13', 'القسم', format2)
        sheet.merge_range('C12:C13', 'كود الموظف', format2)
        sheet.merge_range('D12:D13', 'الموظف', format2)
        sheet.merge_range('E12:E13', 'الوظيفه', format2)
        sheet.merge_range('F12:F13', 'تاريخ الصرف', format2)
        sheet.merge_range('G12:M12', 'الاستحقاقات', format2)
        sheet.write(12, 6, 'المرتب الاساسى', format2)
        sheet.write(12, 7, 'بدل طبيعه العمل ', format2)
        sheet.write(12, 8, 'بدل انتقال ', format2)
        sheet.write(12, 9, 'اجور اضافيه ', format2)
        sheet.write(12, 10, 'بدل سكن ', format2)
        sheet.write(12, 11, 'تسويه رصيد الاجازات ', format2)
        sheet.write(12, 12, 'بدل نهاية الخدمه ', format2)
        sheet.merge_range('N12:N13', 'المرتب الشامل', format2)
        sheet.merge_range('O12:P12', 'الاستقطاعات', format2)
        sheet.write(12, 14, 'استقطاع سلف ', format2)
        sheet.write(12, 15, 'اجمالى الاستقطاعات ', format2)
        sheet.merge_range('Q12:Q13', 'الصافى ', format2)

        data = []
        tot_basic = 0.0
        tot_work = 0.0
        tot_trans = 0.0
        tot_over_pay = 0.0
        tot_eng_house = 0.0
        tot_vaction = 0.0
        tot_service = 0.0
        tot_total = 0.0
        tot_net = 0.0
        tot_loan = 0.0
        total_ded = 0.0
        for employee in employees:
            if state in ['draft', 'done']:
                payslip_ids = payslip_obj.search([('employee_id', '=', employee.id),
                                                  ('is_refund', '=', False),
                                                  ('date_from', '<=', to_date),
                                                  ('date_from', '>=', from_date),
                                                  ('state', '=', state)])
            else:
                payslip_ids = payslip_obj.search([('employee_id', '=', employee.id),
                                                  ('is_refund', '=', False),
                                                  ('date_from', '<=', to_date),
                                                  ('date_from', '>=', from_date)])

            if not payslip_ids:
                continue
            basic = 0.0
            work = 0.0
            trans = 0.0
            over_pay = 0.0
            eng_house = 0.0
            vaction = 0.0
            service = 0.0
            total = 0.0
            net = 0.0
            loan = 0.0

            for payslip in payslip_ids:
                payslip_lines_ids = payslip_line_obj.search([('slip_id', '=', payslip.id)])
                if not payslip_lines_ids:
                    continue

                for payslip_line_rec in payslip_lines_ids:
                    if payslip_line_rec.salary_rule_id.id in salary_rules:
                        if payslip_line_rec.salary_rule_id.code == 'BASIC':
                            basic += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'housing':
                            eng_house += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'WORKALW':
                            work += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'AnnualLeave':
                            vaction += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'EndOfService':
                            service += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'transportion':
                            trans += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'OTHERALW':
                            over_pay += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'LOAN':
                            loan += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'NET':
                            net += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'GROSS':
                            total += payslip_line_rec.total
            tot_ded = total - net
            data_list = [employee.work_location or ' ', employee.department_id.name or ' ', employee.employee_id or ' ',
                         employee.name or ' ', employee.job_id.name or ' ', str(payslip.create_date)[:10] or ' ',
                         basic or 0.0, work or 0.0, trans or 0.0, over_pay or 0.0, eng_house or 0.0, vaction or 0.0,
                         service or 0.0, total or 0.0, loan or 0.0, tot_ded or 0.0, net or 0.0]

            data.append(data_list)
            tot_basic += basic
            tot_work += work
            tot_trans += trans
            tot_over_pay += over_pay
            tot_eng_house += eng_house
            tot_vaction += vaction
            tot_service += service
            tot_total += total
            tot_net += net
            tot_loan += loan
            total_ded += tot_ded
        data.append(['الاجمالى العام', ' ', ' ', ' ', ' ', ' ', tot_basic or 0.0, tot_work or 0.0, tot_trans or 0.0,
                     tot_over_pay or 0.0, tot_eng_house or 0.0, tot_vaction or 0.0, tot_service or 0.0,
                     tot_total or 0.0, tot_loan or 0.0, total_ded or 0.0, tot_net or 0.0])
        for index, record in enumerate(data):
            col = -1
            for line in record:
                col += 1
                sheet.write(index + 13, col, line, format1)
