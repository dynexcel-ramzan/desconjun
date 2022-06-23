# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
import cx_Oracle


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'
    
    
    attendance_date_type = fields.Selection([
        ('in_time', 'IN time'),
        ('out_time', 'Out Time'),
        ],
        readonly=False, string='Attendance Date Type', index=True , default='in_time')
    