# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage = fields.Monetary('Basic Salary', digits=(16, 2), required=True, track_visibility="onchange",
                           help="Employee's monthly gross Basic Salary.")

    transportation_allowance = fields.Float('انتقاﻻت',
                                            digits_compute=dp.get_precision('Payroll'),
                                            help="Allowance towards Transportation")
    housing_allowance = fields.Float('سكن',
                                     digits_compute=dp.get_precision('Payroll'),
                                     help="Allowance towards Housing")
    mobile_allowance = fields.Float('اتصال',
                                    digits_compute=dp.get_precision('Payroll'),
                                    help="Allowance towards Mobile")
    overtime_allowance = fields.Float('عمل اضافى',
                                      digits_compute=dp.get_precision('Payroll'),
                                      help="Allowance towards OverTime")
    work_allowance = fields.Float('طبيعه العمل',
                                  digits_compute=dp.get_precision('Payroll'),
                                  help="Allowance towards Mobile")
    reward = fields.Float('مكافأه',
                          digits_compute=dp.get_precision('Payroll'),
                          help="Reward")
    other_allowance = fields.Float('آخرى',
                                   digits_compute=dp.get_precision('Payroll'))
    deduction = fields.Float('خصةمات',
                                   digits_compute=dp.get_precision('Payroll'))


    is_trans = fields.Boolean(string="نسبه مئويه")
    is_house = fields.Boolean(string="نسبه مئويه")
    is_mobile = fields.Boolean(string="نسبه مئويه")
    is_over = fields.Boolean(string="نسبه مئويه")
    is_work = fields.Boolean(string="نسبه مئويه")
    is_reward = fields.Boolean(string="نسبه مئويه")
    is_other = fields.Boolean(string="نسبه مئويه")

    emp_id = fields.Char(string="Employee ID", related='employee_id.employee_id', required=False, )
    gosi = fields.Float(string="Gosi Saudi", compute='_compute_gosi', readonly='0', required=False, default=0.0)
    gosi_in_payslip = fields.Boolean(string="Gosi Not Appear In PaySlip", )
    country_name = fields.Char(string="Nationality", related='employee_id.country_id.code', required=False, )

    @api.one
    def _compute_gosi(self):
        for record in self:
            if record.employee_id.country_id.code == 'SA':
                if record.is_house == False:
                    record.gosi = (record.wage + record.housing_allowance) * 0.10
                else:
                    record.gosi = (record.wage + (record.wage * record.housing_allowance / 100)) * 0.10
