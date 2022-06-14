# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
   

    hobby_type = fields.Selection(selection=[
            ('hiking', 'Hiking'),
            ('traveling', 'Traveling'),
            ('workout', 'Workout'),
        ], string='Hobbies', tracking=True,
        default='hiking')