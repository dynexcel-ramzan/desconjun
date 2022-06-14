# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PFLedgerType(models.Model):
    _name = 'pf.ledger.type'
    _description = 'PF Ledger Type'
    
    name = fields.Char(string='Name')
    

