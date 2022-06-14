# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    @api.constrains('cost_center_information_line')
    def _check_cost_center_information(self):
        for line in self:
            total_percentage_distribute = 0 
            inner_count = 0
            for cost_line in line.cost_center_information_line:
                inner_count += 1
                if inner_count==1:
                    cost_line.update({'by_default': True })    
                total_percentage_distribute += cost_line.percentage_charged
            if total_percentage_distribute > 100 or total_percentage_distribute < 100:
                raise UserError(' Cost Center Distribution must equal to 100! ')
    
    

class CostInformationLine(models.Model):
    _inherit = 'cost.information.line'
    
    
    controlled_id = fields.Many2one('controlled.account', string='Control-Account', required=True)
    by_default = fields.Boolean(string='By Default')

    
        
    
    
