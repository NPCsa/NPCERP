# -*- coding: utf-8 -*-

from odoo import models


class PayrollXlsx(models.AbstractModel):
    _name = 'report.odt_payslip_company_report.report_payroll_company_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, payslips):
        salary_rules = self.env['hr.salary.rule']
        employees = False
        from_date = ''
        to_date = ''
        for line in payslips:
            employees = line.employee_ids or self.env['hr.employee'].search([])
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
        sheet.set_column(0, 25, 20)
        sheet.insert_image('B2', '../static/images/logo.jpeg')

        sheet.merge_range('H7:O7', 'كشف المرتبات', format2)
        sheet.merge_range('H8:I8', 'التاريخ ', format2)
        sheet.merge_range('L10:K10', str('Payslips Status ' + str(state)), format2)
        sheet.merge_range('J8:O8', str(' من  ' + str(from_date) + 'الى  ' + str(to_date)), format2)
        sheet.merge_range('A12:A13', 'كود الموظف', format2)
        sheet.merge_range('B12:B13', 'الموظف', format2)
        sheet.merge_range('C12:C13', 'الادارة', format2)
        sheet.merge_range('D12:D13', 'القسم', format2)
        sheet.merge_range('E12:E13', 'الوظيفه', format2)
        sheet.merge_range('F12:F13', 'تاريخ الصرف', format2)
        sheet.merge_range('G12:N12', 'الاستحقاقات', format2)
        sheet.write(12, 6, 'المرتب الاساسى', format2)
        sheet.write(12, 7, 'سكن ', format2)
        sheet.write(12, 8, 'انتقال ', format2)
        sheet.write(12, 9, 'اتصال ', format2)
        sheet.write(12, 10, 'عمل اضافى ', format2)
        sheet.write(12, 11, 'طبيعه العمل ', format2)
        sheet.write(12, 12, 'مكافأه ', format2)
        sheet.write(12, 13, 'اخري ', format2)
        sheet.merge_range('O12:O13', 'المرتب الشامل', format2)
        sheet.merge_range('P12:U12', 'الاستقطاعات', format2)
        sheet.write(12, 15, ' تامينات ', format2)
        sheet.write(12, 16, ' غياب وتاخير ', format2)
        sheet.write(12, 17, ' سلف ', format2)
        sheet.write(12, 18, ' احازه استثنائيه ', format2)
        sheet.write(12, 19, ' جزاءات ', format2)
        sheet.write(12, 20, ' اخري ', format2)
        sheet.merge_range('V12:V13', 'اجمالى الاستقطاعات ', format2)
        sheet.merge_range('W12:W13', 'الصافى ', format2)

        data = []
        tot_basic = 0.0
        tot_trans = 0.0
        tot_house = 0.0
        tot_over = 0.0
        tot_mobile = 0.0
        tot_reward = 0.0
        tot_work = 0.0
        tot_other_alw = 0.0
        tot_gross = 0.0
        tot_gosi = 0.0
        tot_abs_late = 0.0
        tot_loan = 0.0
        tot_unpaid = 0.0
        tot_sanction = 0.0
        tot_other_ded = 0.0
        tot_tot_ded = 0.0
        tot_net = 0.0
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
            trans = 0.0
            house = 0.0
            over = 0.0
            mobile = 0.0
            reward = 0.0
            work = 0.0
            other_alw = 0.0
            gross = 0.0
            gosi = 0.0
            abs_late = 0.0
            loan = 0.0
            unpaid = 0.0
            sanction = 0.0
            other_ded = 0.0
            tot_ded = 0.0
            net = 0.0

            for payslip in payslip_ids:
                payslip_lines_ids = payslip_line_obj.search([('slip_id', '=', payslip.id)])
                if not payslip_lines_ids:
                    continue

                for payslip_line_rec in payslip_lines_ids:
                    if payslip_line_rec.salary_rule_id.id in salary_rules:
                        if payslip_line_rec.salary_rule_id.code == 'BASIC':
                            basic += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'housing':
                            house += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'transportion':
                            trans += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'OVERTIME':
                            over += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'mobile':
                            mobile += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'Reward':
                            reward += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'WORKALW':
                            work += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'OTHERALW':
                            other_alw += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'GROSS':
                            gross += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'GOSI':
                            gosi += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code in ['absence', 'late']:
                            abs_late += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'LOAN':
                            loan += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'unpaid':
                            unpaid += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code in ['SAN', 'other']:
                            sanction += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'OTHERDED':
                            other_ded += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.code == 'NET':
                            net += payslip_line_rec.total
            tot_ded = gross - net
            data_list = [employee.employee_id or ' ',employee.name or ' ',employee.work_location or ' ', employee.department_id.name or ' ', employee.job_id.name or ' ', str(payslip.create_date)[:10] or ' ',
                         basic or 0.0, house or 0.0, trans or 0.0, mobile or 0.0, over or 0.0, work or 0.0,
                         reward or 0.0, other_alw or 0.0, gross or 0.0, gosi or 0.0, abs_late or 0.0,loan or 0.0, unpaid or 0.0,sanction or 0.0,
                         other_ded or 0.0, tot_ded or 0.0, net or 0.0]

            data.append(data_list)
            tot_basic = basic
            tot_trans = trans
            tot_house = house
            tot_over = over
            tot_mobile = mobile
            tot_reward = reward
            tot_work = work
            tot_other_alw = other_alw
            tot_gross = gross
            tot_gosi = gosi
            tot_abs_late = abs_late
            tot_unpaid = unpaid
            tot_sanction = sanction
            tot_other_ded = other_ded
            tot_tot_ded = tot_ded
            tot_net = net
        data.append(['الاجمالى العام', ' ', ' ', ' ', ' ', ' ', tot_basic or 0.0, tot_house or 0.0, tot_trans or 0.0,
                     tot_over or 0.0, tot_mobile or 0.0, tot_reward or 0.0, tot_work or 0.0,
                     tot_other_alw or 0.0, tot_gross or 0.0, tot_gosi or 0.0, tot_abs_late or 0.0,tot_loan or 0.0, tot_unpaid or 0.0,
                     tot_sanction or 0.0, tot_other_ded or 0.0, tot_tot_ded or 0.0, tot_net or 0.0])
        for index, record in enumerate(data):
            col = -1
            for line in record:
                col += 1
                sheet.write(index + 13, col, line, format1)
