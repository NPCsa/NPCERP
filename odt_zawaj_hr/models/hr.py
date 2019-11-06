from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    zw_idara = fields.Many2one('hr.idara', 'Location')
    zw_gosi_reg = fields.Char('GOSI Reg')
    zw_rank = fields.Integer('Rank')
    zw_grade = fields.Integer('Grade')
    iban_number = fields.Char('IBAN Number')
    bank_name = fields.Char('Bank Name')
    swift_number = fields.Char('Swift Number')
    street = fields.Char(string="Street", required=False, )
    district = fields.Char(string="District", required=False, )
    build_no = fields.Char(string="Building NO", required=False, )
    emp_city = fields.Char(string="City", required=False, )
    addition_no = fields.Char(string="Addition NO", required=False, )
    house_type = fields.Char(string="House Type", required=False, )
    zip_code = fields.Char(string="Zip Code", required=False, )
    courses_ids = fields.One2many(comodel_name="hr.training.course", inverse_name="employee_id",
                                  string="Training Courses", required=False, )
    gosi_in_payslip = fields.Boolean(string="Gosi Not Appear In PaySlip", related='contract_id.gosi_in_payslip',store=True)


class TrainingCourse(models.Model):
    _name = 'hr.training.course'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char(string="Course Name", required=False, )
    course_place = fields.Char(string="Course Place", required=False, )
    date_start = fields.Date(string="Start Date ", required=False, )
    date_end = fields.Date(string="End Date", required=False, )
    course_hours = fields.Float(string="Course Hours", required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Payslip", required=False, )


class Idara(models.Model):
    _name = "hr.idara"
    _description = "HR Location"
    _inherit = ['mail.thread']
    _order = "name"
    _rec_name = 'name'

    name = fields.Char('Location Name', required=True)
    employee_ids = fields.One2many(comodel_name="hr.employee", inverse_name="zw_idara", string="Employees",
                                   required=False, )
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)
