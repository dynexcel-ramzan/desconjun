# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class OnHandInventoryReport(models.TransientModel):
    _name = "employee.expense.wizard"
    _description = "Expolyee Expense Report"

    date_from = fields.Date(string='Date From', required=True, default=fields.date.today())
    date_to = fields.Date(string='Date to', required=True, default=fields.date.today())
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    


    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to', 'company_id'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to', 'company_id'])[0])
        return self.env.ref('de_expense_reports.on_employee_expense_report').report_action(self, data=data,
                                                                                                  config=False)