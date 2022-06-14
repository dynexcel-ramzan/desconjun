# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inheri = 'res.partner'
    
    
    partner_sequence = fields.Char(string="Partner ID", default="/", readonly=True, help="Sequence of the parnter")
    
    
    @api.model
    def create(self, vals):
            
        vals['partner_sequence'] = self.env['ir.sequence'].get('res.partner.seq') or ' '
        res_id = super(ResPartner, self).create(vals)
        return res_id