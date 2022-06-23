# -*- coding: utf-8 -*-
# from odoo import http


# class DeShiftType(http.Controller):
#     @http.route('/de_shift_type/de_shift_type/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_shift_type/de_shift_type/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_shift_type.listing', {
#             'root': '/de_shift_type/de_shift_type',
#             'objects': http.request.env['de_shift_type.de_shift_type'].search([]),
#         })

#     @http.route('/de_shift_type/de_shift_type/objects/<model("de_shift_type.de_shift_type"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_shift_type.object', {
#             'object': obj
#         })
