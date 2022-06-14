# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class de_expense_reports(models.Model):
#     _name = 'de_expense_reports.de_expense_reports'
#     _description = 'de_expense_reports.de_expense_reports'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
