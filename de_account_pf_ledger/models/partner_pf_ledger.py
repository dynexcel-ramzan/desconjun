# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PartnersPFLedger(models.Model):
    _name = 'partner.pf.ledger'
    _description = 'Partner PF Ledger'
    _rec_name = 'employee_id'
    
    name = fields.Char(string='Period')
    date = fields.Date(string='Date', required=True)
    description = fields.Char(string='Description')
    type_id = fields.Many2one('pf.ledger.type', string='Type', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    debit = fields.Float(string='Debit')
    credit = fields.Float(string='Credit')
    balance = fields.Float(string='Balance')
    company_id = fields.Many2one('res.company', string='Company')

    @api.constrains('date')
    def _check_date(self):
        for line in self:
            line.company_id = line.employee_id.company_id.id
            line.description = line.type_id.name
            line.balance = line.debit - line.credit
            line.name = line.date.strftime('%b-%y')


    
    

