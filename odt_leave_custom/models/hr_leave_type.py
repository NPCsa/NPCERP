# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class LeaveType(models.Model):
    _inherit = 'hr.leave.type'

    code = fields.Char(
        string='Leave Code',
        required=True, 
    )
    
    _sql_constraints = [
        (
            'leave_code',
            'UNIQUE (code)',
            _('The Leave Code is Unique')
        )
    ]

    
    
    

    
