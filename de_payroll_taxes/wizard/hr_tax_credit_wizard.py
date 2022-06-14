# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _get_available_contracts_domain(self):
        return [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]

    def _get_employees(self):
        active_employee_ids = self.env.context.get('active_employee_ids', False)
        exist_payslips = self.env['hr.payslip'].search([('fiscal_month','=',fields.date.today().month)])
        if active_employee_ids:
            return self.env['hr.employee'].search([('id', 'not in', exist_payslips.employee_id.ids), ('bank_account_id','!=',False),('active', '=', True),('stop_salary','=',False),('contract_ids.state', '=', 'open'), ('company_id', '=', self.env.company.id)])
        # YTI check dates too
        return self.env['hr.employee'].search([('id', 'not in', exist_payslips.employee_id.ids),('bank_account_id','!=',False), ('contract_ids.state', '=', 'open'),('active', '=', True),('stop_salary','=',False),('company_id', '=', self.env.company.id)])
    

class HrTaxCreditWizard(models.TransientModel):
    _name = 'hr.tax.credit.wizard'
    _description='Tax Credit Wizard'
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Date(string='Start Date', required=True)
    credit_amount = fields.Float(string='Credit Amount')
    number_of_month = fields.Integer(string='Number Of Month', default=1)
    remarks = fields.Char(string='Remarks')
    credit_type_id = fields.Many2one('tax.credit.type', string='Tax Credit Type', required=True)

    
    def action_create_tax_credit(self):
        for line in self:
            period=line.date
            count = 0
            for ext_rang in range(self.number_of_month):
                count +=1
                if count > 1:
                    period=period+timedelta(31)
                vals={
                    'name': line.employee_id.name +' ('+str(line.employee_id.emp_number)+')',
                    'employee_id': line.employee_id.id,
                    'date': period,
                    'fiscal_month': period.month,
                    'tax_year': period.year,
                    'tax_amount': (line.credit_amount/line.number_of_month),
                    'company_id': line.employee_id.company_id.id,
                    'remarks': line.remarks,
                    'dist_month': line.number_of_month,
                    'post': 'N',
                    'credit_type_id': line.credit_type_id.id,
                }
                tax_credit=self.env['hr.tax.credit'].create(vals)
    
    
    
    
    
    
 
    
    
    

