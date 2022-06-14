# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    expense_percent = fields.Float(string='Salary(%) Expense Limit(Contract)')
    expense_amt_limit = fields.Float(string='Expense Amount Limit(Contract)')

    

