# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProdcutTemplate(models.Model):
    _inherit = 'product.template'
    
    
    
    location_ids = fields.Many2many('stock.location', string='Locations')
    
    
    @api.model
    def create(self, vals):
        res_id = super(ProdcutTemplate, self).create(vals)
        res_id.action_check_locations()
        return res_id
    
    
    def action_check_locations(self):
        for line in self:
            line.location_ids = self.env['stock.location'].search([], limit=3).ids
