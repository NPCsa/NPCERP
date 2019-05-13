# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class DateNotice(models.Model):
    _name = 'hr.effective.date'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True)
    emp_id = fields.Char(string="Employee ID", related='employee_id.employee_id', required=False, )
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    start_work = fields.Date(string="Return Working Date", required=True)
    note = fields.Text(string="Notes", required=False)
    absent_from = fields.Date(string="From", required=False, )
    absent_to = fields.Date(string="To", required=False, )
    absent_days = fields.Integer(string="Days", required=False, )
    state = fields.Selection([('draft', _('Draft')),
                              ('cancel', _('Cancelled')),
                              ('submit', _('Submit')),
                              ('confirm', _('Approved'))
                              ], _('Status'), default='draft',
                             help=_("Gives the status"))

    @api.multi
    def button_submit(self):
        self.state = 'submit'

    @api.multi
    def button_confirm(self):
        holiday_obj = self.env['hr.leave']
        employee = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
        if self.start_work < employee.return_work:
            return_date = datetime.strptime(self.start_work, "%Y-%m-%d").date()
            return_dt = str(return_date) + " 00:00:00"
            vacation = self.env['hr.leave'].search(
                [('employee_id', '=', self.employee_id.id),('date_to', '>', return_dt),
                 ('state', '=', 'validate')])
            emp_id = ''
            name = ''
            leave_type = ''
            start_dt = ''
            end_dt = ''
            days = ''
            for vac in vacation:
                vac_f_date = datetime.strptime(vac.date_from, "%Y-%m-%d %H:%M:%S").date()
                to_date = datetime.strptime(return_dt, "%Y-%m-%d %H:%M:%S").date()
                days = (to_date - vac_f_date).days
                emp_id = vac.employee_id
                name = vac.name
                leave_type = vac.holiday_status_id
                start_dt = vac.date_from
                end_dt = datetime.strptime(str(to_date + timedelta(days=-1)) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
                vac.action_refuse()
                vac.action_reset()
                vac.unlink()
                holiday = holiday_obj.create({
                    'name': name,
                    'state': 'validate',
                    'employee_id': emp_id.id,
                    'date_from': start_dt,
                    'date_to': end_dt,
                    'number_of_days': days,
                    'holiday_status_id': leave_type.id,
                    'department_id': emp_id.department_id.id,
                })
                holiday.action_validate()
            if employee.on_vacation == True:
                employee.write({'on_vacation': False, 'return_work': return_date})
        elif self.start_work == employee.return_work:
            if employee.on_vacation == True:
                employee.write({'on_vacation': False})
        else:
            st_dt = datetime.strptime(self.start_work, "%Y-%m-%d")
            ret_dt = str(st_dt + timedelta(days=-1))
            vacation = self.env['hr.leave'].search(
                [('employee_id', '=', self.employee_id.id), ('type', '=', 'remove'), ('date_to', '>=', ret_dt),
                 ('state', '=', 'validate')])
            if vacation:
                if employee.on_vacation == True:
                    employee.write({'on_vacation': False, 'return_work': self.start_work})
            else:
                start_w_date = datetime.strptime(self.start_work, "%Y-%m-%d").date()
                ret_date = datetime.strptime(employee.return_work, "%Y-%m-%d").date()
                absent_days = (start_w_date - ret_date).days
                if employee.on_vacation == True:
                    employee.write(
                        {'on_vacation': False, 'return_work': start_w_date,
                         'absent_ids': {'absent_from': ret_date, 'absent_to': start_w_date + timedelta(days=-1),
                                        'absent_days': absent_days}})

                    employee.absent_ids[-1].write(
                        {'absent_from': ret_date, 'absent_to': start_w_date + timedelta(days=-1),
                         'absent_days': absent_days})
        self.state = 'confirm'

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'
