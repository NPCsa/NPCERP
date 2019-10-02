# -*- coding:utf-8 -*-

import pytz
from datetime import datetime, date

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


def get_current_year(context):
    if not context:
        context = {}
    tz = context.get('tz', False)
    tz = tz and pytz.timezone(tz) or pytz.utc
    return datetime.now(tz).year


class termination(models.TransientModel):
    _name = 'hr.ter.holiday.wiz'

    department_ids = fields.Many2many(comodel_name="hr.department", string="Departments", )
    location_ids = fields.Many2many(comodel_name="hr.idara", string="Location", )
    report_option = fields.Selection(string="Type", selection=[('all', 'All'), ('department', 'Department'),
                                                               ('location', 'Location'), ], required=True, default="all")

    start_date = fields.Datetime(
        'From Date',
        default=lambda self: (
            date(get_current_year(self.env.context), 1, 1).strftime(
                DEFAULT_SERVER_DATE_FORMAT))
    )
    end_date = fields.Datetime(
        'To Date',
        default=lambda self: (
            date(get_current_year(self.env.context), 12, 31).strftime(
                DEFAULT_SERVER_DATE_FORMAT))
    )
    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.env.context.get('active_ids', []),
            'model': 'hr.holiday.termination',
            'form': data
        }
        return self.env.ref('odt_termination_report_filter.action_report_termination_holiday').report_action(self, data=datas)
