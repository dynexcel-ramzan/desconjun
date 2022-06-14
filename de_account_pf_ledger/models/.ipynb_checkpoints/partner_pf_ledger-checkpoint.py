# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PartnersPFLedger(models.Model):
    _name = 'partner.pf.ledger'
    _description = 'Partner PF Ledger'
    
    name = fields.Char(string='Period')
    date = fields.Date(string='Date')
    description = fields.Char(string='Description')
    type_id = fields.Many2one('pf.ledger.type', string='Type', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    debit = fields.Float(string='Debit')
    credit = fields.Float(string='Credit')
    balance = fields.Float(string='Balance')
    company_id = fields.Many2one('res.company', string='Company')
    

