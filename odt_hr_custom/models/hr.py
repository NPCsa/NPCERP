
from datetime import datetime
from odoo import models, api, fields

class EmployeeType(models.Model):
    _name = 'hr.employee.type'
    name = fields.Char(string='Name')

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.one
    @api.depends('birthday')
    def compute_age(self):
        for emp in self:
            if emp.birthday:
                today = fields.date.today()
                born = datetime.strptime(str(emp.birthday), '%Y-%m-%d')
                self.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    employee_type = fields.Many2one('hr.employee.type', 'Employee Type')
    work_address = fields.Char(string="Work Address")
    employee_grade = fields.Many2one('hr.employee.grade', 'Employee Grade')
    employee_status_id = fields.Many2one('hr.status', 'Employee Status', required=False)
    religion_id = fields.Many2one('hr.religion', 'Religion', required=False)
    age = fields.Char('Age', compute='compute_age')
    place_of_birth = fields.Many2one('res.country', 'Country', ondelete='restrict')
    place_of_birth_city = fields.Char('City', translate=True, required=False)
    nationality = fields.Char('Nationality', translate=True, required=False)
    identification_id = fields.Char('ID', required=False)
    identification_type = fields.Selection(string="Identification Type",
                                           selection=[('iqama', 'Iqama'), ('national_id', 'National ID')],
                                           default='iqama', required=False, )
    entry_number = fields.Char('Entry Number')
    iqama_date_of_issue = fields.Date('Date of Issue', required=False)
    iqama_date_of_expiry = fields.Date('Date of Expiry', required=False)
    # iqama_issuing_authority = fields.Char('Issuing Authority', translate=True, required=False)
    iqama_issuing_city = fields.Char('Issuing City', translate=True, required=False)
    sponsor_type = fields.Selection([('jihan', 'Jehan'), ('other', 'Other')], default='other', string='Sponsor Type')
    sponsor_id = fields.Char('Sponsor ID', translate=True, required=False)
    sponsor_name = fields.Char('Sponsor Name', translate=True, required=False)
    passport_issuing_authority = fields.Char('Issuing Authority', translate=True, required=False)
    passport_date_of_issue = fields.Date('Date of Issue', required=False)
    passport_date_of_expiry = fields.Date('Date of Expiry', required=False)
    joining_date = fields.Date('Joining Date', required=False)
    mobile_phone_2 = fields.Char('Mobile-2 No')
    educational_level_id = fields.Many2one('hr.education.level', 'Education Level', required=False)
    family_member_ids = fields.One2many('hr.family', 'employee_id', 'Family Details')
    insurance_ids = fields.One2many('hr.insurance', 'employee_id', 'Insurance Details')
    trail_from = fields.Date(string='Trail Period From')
    trail_to = fields.Date(string='Trail Period To')


    @api.multi
    def send_email_iqama(self):
        email = self.browse(self.id).work_email
        email_template_obj = self.env['email.template']
        template_ids = email_template_obj.search([('name', '=', 'Iqama Expiration Alert')])
        email_template_obj.write(template_ids, {'email_to': email})
        if template_ids:
            values = email_template_obj.generate_email(template_ids[0], self.id)
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                mail_mail_obj.send([msg_id])
        return True

    @api.multi
    def send_email_passport(self):
        email = self.browse(self.id).work_email
        email_template_obj = self.env['email.template']
        template_ids = email_template_obj.search([('name', '=', 'Passport Expiration Alert')])
        email_template_obj.write(template_ids, {'email_to': email})
        if template_ids:
            values = email_template_obj.generate_email(template_ids[0], self.id)
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                mail_mail_obj.send([msg_id])
        return True

    @api.multi
    def send_email_contract(self):
        email = self.browse(self.id).work_email
        email_template_obj = self.env['email.template']
        template_ids = email_template_obj.search([('name', '=', 'Contract Expiration Alert')])
        email_template_obj.write(template_ids, {'email_to': email})
        if template_ids:
            values = email_template_obj.generate_email(template_ids[0], self.id)
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                mail_mail_obj.send([msg_id])
        return True

    @api.multi
    def send_email_insurance(self):
        email = self.browse(self.id).work_email
        email_template_obj = self.env['email.template']
        template_ids = email_template_obj.search([('name', '=', 'Insurance Expiration Alert')])
        email_template_obj.write(template_ids, {'email_to': email})
        if template_ids:
            values = email_template_obj.generate_email(template_ids[0], self.id)
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                mail_mail_obj.send([msg_id])
        return True

    @api.multi
    def send_email_trail(self):
        email = self.browse(self.id).work_email
        email_template_obj = self.env['email.template']
        template_ids = email_template_obj.search([('name', '=', 'Trail Expiration Alert')])
        email_template_obj.write(template_ids, {'email_to': email})
        if template_ids:
            values = email_template_obj.generate_email(template_ids[0], self.id)
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                mail_mail_obj.send([msg_id])
        return True





class HrStatus(models.Model):
    _name = 'hr.status'

    name = fields.Char('Name', required=True, translate=True)


class HrEmployeeGrade(models.Model):
    _name = 'hr.employee.grade'

    name = fields.Char('Name', required=True, translate=True)


class HrReligion(models.Model):
    _name = 'hr.religion'

    name = fields.Char('Name', required=True, translate=True)


class HrEducationLevel(models.Model):
    _name = 'hr.education.level'

    name = fields.Char('Name', required=True, translate=True)


class HrInsurance(models.Model):
    _name = 'hr.insurance'

    insurance_type_id = fields.Many2one('hr.insurance.type', 'Insurance Type')
    insurance_company_id = fields.Many2one('hr.insurance.company', 'Insurance Company')
    employee_id = fields.Many2one('hr.employee', ondelete='cascade')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    booking_no = fields.Char(string="Booking NO", required=False, )
    member_no = fields.Char(string="Membership NO", required=False, )
    policy_no = fields.Char(string="Policy NO", required=False, )


class HrInsuranceType(models.Model):
    _name = 'hr.insurance.type'

    name = fields.Char('Name', required=True, translate=True)


class HrInsuranceCompany(models.Model):
    _name = 'hr.insurance.company'

    name = fields.Char('Name', required=True, translate=True)
