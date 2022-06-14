# -*- coding: utf-8 -*-
# from odoo import http


# class DeExpenseReports(http.Controller):
#     @http.route('/de_expense_reports/de_expense_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_expense_reports/de_expense_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_expense_reports.listing', {
#             'root': '/de_expense_reports/de_expense_reports',
#             'objects': http.request.env['de_expense_reports.de_expense_reports'].search([]),
#         })

#     @http.route('/de_expense_reports/de_expense_reports/objects/<model("de_expense_reports.de_expense_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_expense_reports.object', {
#             'object': obj
#         })
