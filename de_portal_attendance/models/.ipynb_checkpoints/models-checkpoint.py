# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class HrAttendance(models.Model):
    _inherit = 'hr.attendance' 
    
    
    is_portal_modify = fields.Boolean(string='Modification')
    modify_type = fields.Selection(selection=[
            ('in', 'in'),
            ('out', 'out'),
        ], string='Modify Type',
        )
    
    
    in_validity = fields.Selection(selection=[
            ('valid', 'Valid'),
            ('invalid', 'In-Valid'),
        ], string='In Validity',
        default='valid')
    in_type_validity = fields.Selection(selection=[
            ('in', 'In'),
            ('out', 'Out'),
        ], string='In Type',
        default='in')
    
    in_date = fields.Date(string='In Date')
    
    out_date = fields.Date(string='Out Date')
    out_type_validity = fields.Selection(selection=[
            ('in', 'In'),
            ('out', 'Out'),
        ], string='Out Type',
        default='out')
    out_validity = fields.Selection(selection=[
            ('valid', 'Valid'),
            ('invalid', 'In-Valid'),
        ], string='Out Validity',
        default='valid')

    
    
    #def action_check_write_date(self):
    #    for line in self:
    #        if line.att_date: 
    #            if str(line.att_date ) < '2022-02-16' and self.env.user!=2:
    #                raise UserError('Payroll Workdays Deadline Expire.Please contact HR Department!')
        
    
   # def write(self, values):
   #     result = super(HrAttendance, self).write(values) 
   #     self.action_check_write_date()
   #     return result


    #def action_check_date_create(self):
    #    for line in self:
    #        if line.att_date: 
    #            if str(line.att_date ) < '2022-02-16' and self.env.user!=2:
    #                raise UserError('Payroll Workdays Deadline Expire.Please contact HR Department!')
        
    
    #def create(self, values):
    #    result = super(HrAttendance, self).create(values) 
    #    result.action_check_date_create()
    #    return result
    
    


    

    
    
    

    
