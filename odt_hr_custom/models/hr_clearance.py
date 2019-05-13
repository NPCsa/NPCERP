from odoo import fields, models, api, _
import time
from .. import utils


class hr_clearance(models.Model):
    _name = 'hr.clearance'
    _inherit = 'mail.thread'
    _description = "Employee Clearance"
    _rec_name = 'name'

    @api.one
    def current_logged_employee(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        if employee_id:
            return employee_id
        return False

    @api.multi
    def unlink(self):
        for object in self:
            if object.state in ['confirm', 'done']:
                raise Warning(_('Warning!'), _('You cannot remove the record which is in %s state!') % (object.state))
        return super(hr_clearance, self).unlink()

    @api.model
    def departments_assets(self, department):
        department_asset = []
        assets_ids = self.env['department.asset'].search(
            [('department', '=', department)])
        for asset_id in assets_ids:
            department_asset.append((0, 0, {'department': asset_id.department, 'name': asset_id.name,
                                            'asset_answer': asset_id.asset_answer}))
        return department_asset

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, domain=[('active', '=', True)],
                                  default=current_logged_employee)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Job Title')
    coach_id = fields.Many2one('hr.employee', related='employee_id.coach_id', string='Direct Manager')
    name = fields.Char(related='employee_id.name', string='Name')
    identification_id = fields.Char(related='employee_id.identification_id', string='Employee ID', required=True)
    grade = fields.Char(string='Grade')
    section = fields.Char(string='Section')
    leave_reason = fields.Selection([('resg', 'Resignation'),
                                     ('con_term', 'Contract Termination'),
                                     ('term', 'Termination')], string='Leaving Reason', required=True, default='resg')
    clearance_date = fields.Date('Clearance Date', default=time.strftime('%Y-%m-%d'))
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
                                    readonly=True)
    contact_phone = fields.Char(related='employee_id.address_home_id.phone', string='Phone', readonly="True")
    email = fields.Char(related='employee_id.address_home_id.email', string='Email', readonly="True")
    support_service_asset = fields.One2many('department.asset', 'supp_id', 'Support Services Department',
                                            default=lambda self: self.departments_assets('supp'))
    it_asset = fields.One2many('department.asset', 'it_id', 'IT Department',
                               default=lambda self: self.departments_assets('it'))
    depart_asset = fields.One2many('department.asset', 'emp_dep', 'Employee Department',
                                   default=lambda self: self.departments_assets('dep'))
    gov_public_asset = fields.One2many('department.asset', 'gov_id', 'Gov. & Public Relations Department',
                                       default=lambda self: self.departments_assets('gov'))
    opmarket_asset = fields.One2many('department.asset', 'op_id', 'Operation and Marketing & Sales Department',
                                     default=lambda self: self.departments_assets('op'))
    hr_asset = fields.One2many('department.asset', 'hr_id', 'HR Department',
                               default=lambda self: self.departments_assets('hr'))
    finance_asset = fields.One2many('department.asset', 'finance_id', 'Finance Department',
                                    default=lambda self: self.departments_assets('finance'))

    # employee_3ohda = fields.Many2many(comodel_name="hr.asset.expense.3ohda.line",string="3ohda", required=False, )
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting Approval'),
                              ('done', 'Done'),
                              ('refuse', 'Refused')], 'Status', track_visibility='onchange', default='draft')

    @api.multi
    def print_clearance_form(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        self.sent = True
        return self.env.ref('odt_hr_custom.report_hr_clearance_form').report_action(self)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        employee = self.env['hr.asset.expense.3ohda'].search([('employee_id', '=', self.employee_id.id)])
        if employee:
            self.employee_3ohda = employee.ohda_line.filtered(lambda type : type.state_3ohda == 'deliver').ids

    @api.multi
    def draft_state(self):
        return self.write({'state': 'draft'})

    @api.multi
    def confirm_state(self):
        return self.write({'state': 'confirm'})

    @api.multi
    def approve_state(self):
        return self.write({'state': 'done'})

    @api.multi
    def cancel_state(self):
        return self.write({'state': 'refuse'})


class department_asset(models.Model):
    _name = 'department.asset'
    _description = "Department Assets"
    _rec_name = 'name'

    name = fields.Char('Asset Name', required="True")
    asset_answer = fields.Selection([('YES', 'YES'),
                                     ('NO', 'NO'),
                                     ('No Answer', 'No Answer')], 'Status', required="True")
    reviewed_by = fields.Many2one('hr.employee', 'Handled By')
    it_id = fields.Many2one('hr.clearance', 'IT Department')
    emp_dep = fields.Many2one('hr.clearance', 'Employee Department')
    gov_id = fields.Many2one('hr.clearance', 'Gov. & Public Relations Department')
    op_id = fields.Many2one('hr.clearance', 'Operation and Marketing & Sales Department')
    supp_id = fields.Many2one('hr.clearance', 'Support Services Department')
    hr_id = fields.Many2one('hr.clearance', 'HR Department')
    finance_id = fields.Many2one('hr.clearance', 'Finance Department')
    department = fields.Selection([('dep', 'Employee Department'),
                                   ('gov', 'Gov. & Public Relations')
                                      , ('it', 'IT'), ('op', 'Operation and Marketing & Sales'),
                                   ('supp', 'Support Services Department'),
                                   ('hr', 'HR'),
                                   ('finance', 'Finanace')], 'Department Type')
    notes = fields.Char('Notes')
