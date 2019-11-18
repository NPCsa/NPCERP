from odoo import api, fields, models

class WorkingSchedule(models.Model):
    _inherit = 'resource.calendar.attendance'

    work_type = fields.Selection(string="", selection=[('work', 'Working'), ('weekend', 'Week End'), ], required=False, )
