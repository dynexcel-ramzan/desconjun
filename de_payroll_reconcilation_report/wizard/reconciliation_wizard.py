# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class ReconciliationWizard(models.Model):
    _name = 'reconciliation.wizard'
    _description = 'Reconciliation Wizard'

    company_id = fields.Many2one('res.company',  string='Company', required=True, default=lambda self: self.env.company)
    company_number = fields.Integer(string='Company Code')
    date_from =  fields.Date(string='Previous Month',  default=fields.date.today().replace(day=1)-timedelta(30) )
    date_to =  fields.Date(string='Current Month', required=True,  default=fields.date.today().replace(day=15) )
    
                
    def check_report(self):
        data = {}
        data['form'] = self.read(['company_id','date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['company_id','date_from', 'date_to'])[0])
        return self.env.ref('de_payroll_reconcilation_report.open_payroll_reconciliation_action').report_action(self, data=data, config=False)
