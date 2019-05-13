
from odoo import tools, models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _
from datetime import datetime


class HrFamily(models.Model):
    _name = 'hr.family'
    _description = _('Property Details')

    name = fields.Char('Name', translate=True, required=True)
    identification_type = fields.Selection([('iqama', 'Iqama'), ('national_id', 'National ID')],
                                           default='iqama', required=True)
    date_of_issue = fields.Date('Date of Issue', required=False)
    date_of_expiry = fields.Date('Date of Expiry', required=False)
    identification_no = fields.Char('ID#')
    birthday1 = fields.Date('Birth Day')
    relationship_id = fields.Many2one('hr.family.member.type', 'Relationship', required=True)
    employee_id = fields.Many2one('hr.employee', ondelete='cascade')

    passport_no = fields.Char(string="Passport NO", required=False, )
    place_of_issue_pass = fields.Char(string="Place of issue", required=False, )
    date_of_issue_pass = fields.Date('Date of Issue', required=False)
    date_of_expiry_pass = fields.Date('Date of Expiry', required=False)


class hr_family_memeber_type(models.Model):
    _name = 'hr.family.member.type'

    name = fields.Char('Name', required=True)


