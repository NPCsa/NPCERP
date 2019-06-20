
from datetime import datetime
from odoo import models, api, fields

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('birthday')
    def compute_age(self):
        for partner in self:
            if partner.birthday:
                today = fields.date.today()
                born = datetime.strptime(str(partner.birthday), '%Y-%m-%d')
                self.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                self.age = 0

    name = fields.Char('Name', translate=True, required=True)
    identification_no = fields.Char('National ID/Iqama')
    age = fields.Integer('Age', compute='compute_age')
    birthday = fields.Date('Birth Day')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')


class Company(models.Model):
    _inherit = 'res.company'
    commercial_date = fields.Date(string='Commercial Date')
    municipal_date = fields.Date(string='Municipal License')

    @api.multi
    def send_email_com(self):
        email = self.browse(self.id).email
        email_template_obj = self.env['email.template']
        template_ids = email_template_obj.search([('name', '=', 'Commercial Expiration Alert')])
        email_template_obj.write(template_ids, {'email_to': email})
        if template_ids:
            values = email_template_obj.generate_email(template_ids[0], self.id)
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                mail_mail_obj.send([msg_id])
        return True

    @api.multi
    def send_email_mu(self):
        email = self.browse(self.id).email
        email_template_obj = self.env['email.template']
        template_ids = email_template_obj.search([('name', '=', 'Municipal Expiration Alert')])
        email_template_obj.write(template_ids, {'email_to': email})
        if template_ids:
            values = email_template_obj.generate_email(template_ids[0], self.id)
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                mail_mail_obj.send([msg_id])
        return True


Company()
