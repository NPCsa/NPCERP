# -*- coding: utf-8 -*-

from odoo import models

class PayrollXlsx(models.AbstractModel):

    _name = 'report.odt_bank_ahli_no1_report.report_bank_ahli_n1_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, payslips):

        payslip_ids = []
        all_payslip = []
        state = ''
        for line in payslips:
            state = line.state
            for payslip in line.batch_id.filtered(lambda pay: pay.slip_ids):
                payslip_ids.append(payslip.slip_ids.ids)
            payslip_ids.append(line.payslip_id.ids)

        for payslip in payslip_ids:
            for line in payslip:
                all_payslip.append(line)
        all_payslip = list(set(all_payslip))
        payslip_ids = self.env['hr.payslip'].browse(all_payslip).filtered(lambda pay: pay.is_refund == False)
        salary_rules = self.env['hr.salary.rule'].search([]).sorted(
            key=lambda v: v.sequence).ids
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

        sheet.set_column(0, 10, 20)
        sheet.write(1, 4, 'Status', format2)
        sheet.write(1, 5, str(state), format2)
        sheet.write(4, 0, 'Bank', format2)
        sheet.write(4, 1, 'Account Number', format2)
        sheet.write(4, 2, 'Total Salary', format2)
        sheet.write(4, 3, 'Transaction Reference', format2)
        sheet.write(4, 4, 'Employee Name', format2)
        sheet.write(4, 5, 'National ID/Iqama ID', format2)
        sheet.write(4, 6, 'Employee Address', format2)
        sheet.write(4, 7, 'Basic Salary', format2)
        sheet.write(4, 8, 'Housing Allowance', format2)
        sheet.write(4, 9, 'Other Earnings', format2)
        sheet.write(4, 10, 'Deduction', format2)



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
            other = 0.0
            total = 0.0

            payslip_lines_ids = payslip_line_obj.search([('slip_id', '=', payslip.id)])
            if not payslip_lines_ids:
                continue

            for payslip_line_rec in payslip_lines_ids:
                if payslip_line_rec.salary_rule_id.id in salary_rules:
                    if payslip_line_rec.salary_rule_id.code == 'BASIC':
                        basic += payslip_line_rec.total
                    elif payslip_line_rec.salary_rule_id.code == 'housing':
                        housing += payslip_line_rec.total
                    elif payslip_line_rec.salary_rule_id.code == 'NET':
                        net += payslip_line_rec.total
                    elif payslip_line_rec.salary_rule_id.code == 'GROSS':
                        total += payslip_line_rec.total
            deduction = total - net
            other = total - basic - housing
            data_list = [payslip.employee_id.bank_name or ' ',payslip.employee_id.iban_number or ' ',net, payslip.employee_id.employee_id, payslip.employee_id.name, payslip.employee_id.identification_id or ' ',
                         payslip.employee_id.emp_city or ' ',basic, housing,other, deduction]
            tot_net += net
            tot_basic += basic
            tot_housing += housing
            tot_other += other
            tot_ded += deduction


            all_data.append(data_list)
        data_tot_list = ['Total',' ', tot_net, ' ', ' ',' ',' ', tot_basic, tot_housing,tot_other, tot_ded]
        all_data.append(data_tot_list)
        for index, record in enumerate(all_data):
            col = -1
            for line in record:
                col += 1
                sheet.write(index + 5, col, line, format1)
