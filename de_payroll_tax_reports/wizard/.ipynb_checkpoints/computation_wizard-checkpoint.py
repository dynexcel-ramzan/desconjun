# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta



class TaxComputationWizard(models.Model):
    _name = 'tax.computation.wizard'
    _description = 'Tax Computation Wizard'
     

    company_id = fields.Many2one('res.company',  string='Company', required=True, default=lambda self: self.env.company )
    company_number = fields.Integer(string='Company Code')
    employee_id = fields.Many2one('hr.employee',  string='Employee', required=True, domain='[("company_id","=",company_id)]' )
    date_from =  fields.Date(string='Month From', required=True, default=fields.date.today().replace(month=7,day=1, year=fields.date.today().year-1))
    date_to =  fields.Date(string='Month To', required=True, default=fields.date.today().replace(day=30)  )
    
    
    
    def check_report(self):
        data = {}
        data['form'] = self.read(['company_id','date_from', 'date_to','employee_id'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['company_id','date_from', 'date_to','employee_id'])[0])
        return self.env.ref('de_payroll_tax_reports.open_tax_computation_action').report_action(self, data=data, config=False)
