# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountPfLedger(http.Controller):
#     @http.route('/de_account_pf_ledger/de_account_pf_ledger/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_pf_ledger/de_account_pf_ledger/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_pf_ledger.listing', {
#             'root': '/de_account_pf_ledger/de_account_pf_ledger',
#             'objects': http.request.env['de_account_pf_ledger.de_account_pf_ledger'].search([]),
#         })

#     @http.route('/de_account_pf_ledger/de_account_pf_ledger/objects/<model("de_account_pf_ledger.de_account_pf_ledger"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_pf_ledger.object', {
#             'object': obj
#         })
