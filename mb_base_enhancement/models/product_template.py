# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProdcutTemplate(models.Model):
    _inherit = 'product.template'
    
    
    
    location_ids = fields.Many2many('stock.location', string='Locations')
    
    
    
    
