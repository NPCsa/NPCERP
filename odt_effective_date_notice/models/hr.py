
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime , timedelta
from odoo.exceptions import Warning

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fixed_overtime = fields.Float(string="Fixed OverTime",  required=False, )
    on_vacation = fields.Boolean(string="On Vacation")
    start_vacation = fields.Date(string="start Vacation", required=False, )
    expect_return_work = fields.Date(string="Expected Return Date", required=False, )
    return_work = fields.Date(string="Return Date", required=False, )

class HrHolidays(models.Model):
    _inherit = 'hr.leave'

    return_date = fields.Date(string="Return Date", required=False)
    effective_id = fields.Many2one(comodel_name="hr.effective.date", string="Effective Notice", required=False, )

    @api.multi
    def action_validate(self):
        data_holiday = self.browse(self._ids)
        for record in data_holiday:
            if record.date_to is not False:
                effectives = self.env['hr.effective.date']
                effective_dates = effectives.sudo().search(
                    [('employee_id', '=', record.employee_id.id), ('vacation_id', '!=', record.id),
                     ('state', 'in', ['draft', 'submit'])])
                if effective_dates:
                    raise Warning(_(
                        'you can not validate vacation because there is effective date notice not confirmed %s') % record.employee_id.name)
                start_date = datetime.strptime(str(record.date_from)[:10], "%Y-%m-%d")
                return_date = datetime.strptime(str(record.date_to)[:10], "%Y-%m-%d")
                record.employee_id.sudo().write({'on_vacation': True, 'start_vacation': start_date,
                                          'return_work': return_date + timedelta(days=+1),
                                          'expect_return_work': return_date + timedelta(days=+1)})
                if not record.effective_id:
                    vals = {
                        'employee_id': record.employee_id.id,
                        'vacation_id': record.id,
                        'start_work': return_date + timedelta(days=+1),
                    }
                    effective_id = effectives.sudo().create(vals)
                    record.effective_id = effective_id.id
        return super(HrHolidays, self).action_validate()

    @api.multi
    def action_refuse(self):
        data_holiday = self.browse(self._ids)
        for record in data_holiday:
            if record.date_to is not False:
                if record.effective_id.state == 'confirm':
                    raise Warning(_('you can not refuse this leave because has effective date confirmed'))
                else:
                    record.return_date = False
        return super(HrHolidays, self).action_refuse()

