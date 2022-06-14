# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta



class TaxCertificateWizard(models.Model):
    _name = 'tax.certificate.wizard'
    _description = 'Tax Certificate Wizard'

    company_id = fields.Many2one('res.company',  string='Company', required=True, default=lambda self: self.env.company )
    company_number = fields.Integer(string='Company Code')
    employee_id = fields.Many2one('hr.employee',  string='Employee', required=True,  domain='[("company_id","=",company_id)]' )
    date_from =  fields.Date(string='Month From', required=True, default=fields.date.today().replace(month=7,day=1, year=fields.date.today().year-1))
    date_to =  fields.Date(string='Month To', required=True, default=fields.date.today().replace(day=27) )
    bank = fields.Char(string='Bank')
    branch = fields.Char(string='Branch/City')
    date_of_issue = fields.Date(string='Date of Issue', default=fields.date.today())
    section = fields.Char(string='Section #', default='under section 149 of Income Tax Ordinance, 2001 on account of')
    certificate_line_ids = fields.One2many('tax.certificate.wizard.line', 'certificate_id' , string='Certificate Lines')
    
   
                

    def check_report(self):
        data = {}
        data['form'] = self.read(['company_id','date_from', 'date_to','employee_id','certificate_line_ids','bank','branch'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['company_id','date_from', 'date_to','employee_id','certificate_line_ids','bank','branch'])[0])
        return self.env.ref('de_payroll_tax_reports.open_tax_certificate_action').report_action(self, data=data, config=False)
    
    @api.onchange('date_from', 'date_to','employee_id','bank', 'branch')
    def onchange_date(self):
        for line in self:
            if line.date_from and line.date_to and line.employee_id and line.branch and line.bank:                
                ora_tax_opening = self.env['hr.tax.ded'].sudo().search([('employee_id','=',line.employee_id.id),('date','>=',line.date_from),('date','<=',line.date_to)], order='date asc')
                payslips=self.env['hr.payslip'].search([('employee_id','=',line.employee_id.id),('date_to','>=',line.date_from),('date_to','<=',line.date_to),('tax_year','>','2021'),('state','!=','cancel')], order='date_to asc')
                line.certificate_line_ids.unlink()
                for ora_tax in ora_tax_opening:
                    vals = {
                        'period': ora_tax.date.strftime('%b-%y'),
                        'bank':   line.bank,
                        'branch': line.branch,
                        'amount': round(ora_tax.tax_ded_amount),
                        'certificate_id': line.id,
                    }
                    certificate_line=self.env['tax.certificate.wizard.line'].create(vals)    
                

    
class TaxCertificateWizardline(models.Model):
    _name = 'tax.certificate.wizard.line'
    _description = 'Tax Certificate Wizard Line'
    
    period = fields.Char(string='Period')
    bank = fields.Char(string='Bank')
    branch = fields.Char(string='Branch/City')
    amount = fields.Float(string='Amount', digits=(12, 0))
    certificate_id = fields.Many2one('tax.certificate.wizard', string='Certificate')
    
