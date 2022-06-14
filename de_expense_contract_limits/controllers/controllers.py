# -*- coding: utf-8 -*-
# from odoo import http


# class DeExpenseContractLimits(http.Controller):
#     @http.route('/de_expense_contract_limits/de_expense_contract_limits/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_expense_contract_limits/de_expense_contract_limits/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_expense_contract_limits.listing', {
#             'root': '/de_expense_contract_limits/de_expense_contract_limits',
#             'objects': http.request.env['de_expense_contract_limits.de_expense_contract_limits'].search([]),
#         })

#     @http.route('/de_expense_contract_limits/de_expense_contract_limits/objects/<model("de_expense_contract_limits.de_expense_contract_limits"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_expense_contract_limits.object', {
#             'object': obj
#         })
