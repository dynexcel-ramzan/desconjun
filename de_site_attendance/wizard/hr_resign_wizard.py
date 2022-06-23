
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class HrResignWizard(models.TransientModel):
    _name = "hr.resign.wizard"
    _description = "HR Resign wizard"
    

    resign_date = fields.Date(string='Resign Start Date', required=True)
    effective_date = fields.Date(string='Resign End Date', required=True)  
    resign_type =  fields.Char(string='Resign Type')   
    resign_remarks =  fields.Char(string='Resign Remarks') 
    employee_ids = fields.Many2many('hr.employee', string='Employee')    
    
    def action_update_resign(self):
        for employee in self.employee_ids:
            employee.update({
                'resigned_date':  self.resign_date,
                'effective_date':  self.effective_date,
                'resign_type':  self.resign_type,
                'stop_salary': True, 
                'resigned_remarks': self.resign_remarks,
            })
            if self.effective_date < fields.date.today():
                employee.user_id.update({
                  'active': False,
                })
            contracts=self.env['hr.contract'].search([('employee_id','=',employee.id),('state','=','open')]) 
            for contract in contracts:
                if self.effective_date < fields.date.today():
                    contract.update({
                       'state': 'close',
                       'date_end':  self.effective_date,
                    })
            