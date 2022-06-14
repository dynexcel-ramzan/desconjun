# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ShiftReplceWizard(models.Model):
    _name = 'shift.replace.wizard'
    _description = 'Shift Replace Wizard'
    
    
    replacement_type =fields.Selection(selection=[
            ('fisrt_shift', 'First Shift'),
            ('second_shift', 'Second Shift'),
        ], string='Status', required=True,
        default='fisrt_shift')
    shift_replace_id = fields.Many2one('resource.calendar', string='Shift Replace', required=True)
    shift_replace_with_id = fields.Many2one('resource.calendar', string='Shift Replace With', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    company_id = fields.Many2one('res.company',  string='Company', default=lambda self: self.env.company)
    
    def action_confirm(self):
        for line in self:
            if line.replacement_type=='fisrt_shift':
                shift_schedules = self.env['hr.shift.schedule.line'].search([('company_id','=',line.company_id.id),('date','>=',self.date_from),('date','<=',self.date_to),('first_shift_id','=',self.shift_replace_id.id)])
                for shift_line in shift_schedules:
                    shift_line.update({
                        'first_shift_id': self.shift_replace_with_id.id,
                    })
                    
            if line.replacement_type=='second_shift':
                shift_schedules = self.env['hr.shift.schedule.line'].search([('company_id','=',line.company_id.id),('date','>=',self.date_from),('date','<=',self.date_to),('second_shift_id','=',self.shift_replace_id.id)])
                for shift_line in shift_schedules:
                    shift_line.update({
                        'second_shift_id': self.shift_replace_with_id.id,
                    }) 

