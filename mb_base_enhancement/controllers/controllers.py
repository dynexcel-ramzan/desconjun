# -*- coding: utf-8 -*-
# from odoo import http


# class MbBaseEnhancement(http.Controller):
#     @http.route('/mb_base_enhancement/mb_base_enhancement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mb_base_enhancement/mb_base_enhancement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mb_base_enhancement.listing', {
#             'root': '/mb_base_enhancement/mb_base_enhancement',
#             'objects': http.request.env['mb_base_enhancement.mb_base_enhancement'].search([]),
#         })

#     @http.route('/mb_base_enhancement/mb_base_enhancement/objects/<model("mb_base_enhancement.mb_base_enhancement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mb_base_enhancement.object', {
#             'object': obj
#         })
