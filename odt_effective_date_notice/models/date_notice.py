# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import Warning

class DateNotice(models.Model):
    _name = 'hr.effective.date'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True)
    vacation_id = fields.Many2one(comodel_name="hr.leave", string="Vacation", required=False)
    emp_id = fields.Char(string="Employee ID", related='employee_id.employee_id', required=False, )
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    start_work = fields.Date(string="Return Working Date", required=True)
    note = fields.Text(string="Notes", required=False)
    state = fields.Selection([('draft', _('Draft')),
                              ('cancel', _('Cancelled')),
                              ('submit', _('Submit')),
                              ('confirm', _('Approved'))
                              ], _('Status'), default='draft',
                             help=_("Gives the status"))

    @api.multi
    def button_submit(self):
        employee = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
        if not employee.on_vacation:
            raise Warning(_('This Employee Not On Vacation'))
        self.state = 'submit'

    @api.multi
    def button_confirm(self):
        employee = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
        if employee.on_vacation:
            if self.start_work < employee.return_work:
                return_date = datetime.strptime(str(self.start_work), "%Y-%m-%d").date()
                if employee.on_vacation == True:
                    self.vacation_id.update({'return_date': return_date + timedelta(days=-1)})
                    employee.write({'on_vacation': False, 'return_work': return_date})
            elif self.start_work == employee.return_work:
                if employee.on_vacation == True:
                    return_date = datetime.strptime(str(self.start_work), "%Y-%m-%d").date()
                    self.vacation_id.update({'return_date': return_date + timedelta(days=-1)})
                    employee.write({'on_vacation': False})
            else:
                start_w_date = datetime.strptime(str(self.start_work), "%Y-%m-%d").date()
                if employee.on_vacation == True:
                    self.vacation_id.update({'return_date': start_w_date + timedelta(days=-1)})
                    employee.write(
                        {'on_vacation': False, 'return_work': start_w_date})

            self.state = 'confirm'
        else:
            raise Warning(_('This Employee Not On Vacation'))

    @api.multi
    def button_cancel(self):
        if self.state == 'confirm' and self.vacation_id:
            start_w_date = datetime.strptime(str(self.vacation_id.date_to)[:10], "%Y-%m-%d").date()
            self.vacation_id.update({'return_date': False})
            self.employee_id.write({'on_vacation': True, 'return_work': start_w_date + timedelta(days=+1)})
        self.state = 'cancel'

    @api.multi
    def button_draft(self):
        self.state = 'draft'

    @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'confirm' or record.vacation_id:
                raise Warning(_('You Can not Delete Confirmed Document Or related to vacation'))
        res = super(DateNotice, self).unlink()
        return res
