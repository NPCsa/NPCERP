# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, SUPERUSER_ID
import odoo.addons.decimal_precision as dp


class HrResource(models.Model):
    _inherit = 'resource.resource'
    name = fields.Char('Name', required=False, translate=True)


class hr_employee(models.Model):
    _inherit = "hr.employee"

    @api.model_cr
    def init(self):
        super(hr_employee, self).init()
        self._update_employee_names()

    @api.model
    def split_name(self, name):
        name = u" ".join(name.split(None)) if name else name
        if name:
            parts = name.strip().split(" ", 3)
            if len(parts) < 4:
                for i in range(0, 4 - len(parts)):
                    parts.append(False)

            return {"first_name": parts[0], "second_name": parts[1], "third_name": parts[2], "last_name": parts[3]}

    @api.model
    def _update_employee_names(self):
        employees = self.search(['|',
                                 ('first_name', '=', ' '), ('first_name', '=', False)])
        for ee in employees:
            names = self.split_name(ee.name)
            if names:
                ee.write(names)

    def _firstname_default(self):
        return ' ' if self.env.context.get('module') else False

    first_name = fields.Char('First Name', translate=True, required=False, )
    second_name = fields.Char('Father Name', translate=True, required=False, )
    third_name = fields.Char('Grandfather Name', translate=True, required=False)
    last_name = fields.Char('Last Name', translate=True, required=False, )
    employee_id = fields.Char('Employee ID', required=True, readonly=False, copy=False)

    _sql_constraints = [
        ('employee_id_uniq',
         'UNIQUE (employee_id)',
         'The Employee Code must be unique!')]

    @api.onchange('first_name', 'second_name', 'third_name', 'last_name')
    def _onchange_name(self):
        self.name = self.get_original_name(self.first_name, self.second_name, self.third_name, self.last_name)

    @api.multi
    def get_original_name(self, first_name, second_name, third_name, last_name):
        name = ''
        if first_name:
            name = first_name
        if second_name:
            name += ' ' + second_name
        if third_name:
            name += ' ' + third_name
        if last_name:
            name += ' ' + last_name
        return name

    @api.model
    def create(self, values):
        res = super(hr_employee, self).create(values)
        res.name = self.get_original_name(res.first_name, res.second_name, res.third_name, res.last_name)
        return res

    @api.one
    def write(self, vals):
        for record in self:
            vals['name'] = self.get_original_name(vals.get('first_name', record.first_name),
                                                  vals.get('second_name', record.second_name),
                                                  vals.get('third_name', record.third_name),
                                                  vals.get('last_name', record.last_name))
            return super(hr_employee, self).write(vals)
