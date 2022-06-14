# -*- coding: utf-8 -*-
#################################################################################
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Dynexcel <www.dynexcel.com>

#################################################################################
import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta


class PayrollTaxComputation(models.AbstractModel):
    _name = 'report.de_payroll_tax_reports.computation_report'
    _description = 'Tax Computation Report'

    '''Find payroll Tax Computation Report between the date'''
    @api.model
    def _get_report_values(self, docids, data=None): 
        docs = self.env['tax.computation.wizard'].browse(self.env.context.get('active_id'))
        employee = docs.employee_id
        date_from = docs.date_from
        date_to = docs.date_to
        if not docs.employee_id:
            employee = data['employee']
            date_from = datetime.strptime(str(data['start_date']), "%Y-%m-%d")
            date_to = datetime.strptime(str(data['end_date']), "%Y-%m-%d")  

        payslips=self.env['hr.payslip'].search([('employee_id','=',employee.id),('date_to','>=',date_from),('date_to','<=',date_to),('tax_year','>','2021') ], order='date_to asc')
        salary_rules=self.env['hr.salary.rule'].search([('computation_report','=',True)], order='computation_sequence asc')
        
        ora_tax_opening = self.env['hr.tax.ded'].search([('employee_id','=',employee.id),('date','>=',date_from),('date','<=',date_to),('period_num','<', 7),('tax_year','=','2021') ], order='date asc')
        
        pfund_rule=self.env['hr.salary.rule'].search([('pfund_amount','=',True)], limit=1) 
        contract=self.env['hr.contract'].search([('employee_id','=',employee.id),('state','=','open')], limit=1)
        
        pfund_amount = round((contract.wage/12))
        total_amount_list = []
        
        tax_rebate_detail=[]
        
        total_rule_count = 0 
        for rrule in salary_rules:
            total_rule_count += 1
        
        total_adj_rule_count = 0 
        for rule in salary_rules:
            total_amount=0
            for payslip in payslips:
                for rule_line in payslip.line_ids:
                    if rule.id==rule_line.salary_rule_id.id:
                        total_amount += rule_line.amount
                    if pfund_rule.id==rule_line.salary_rule_id.id:
                        pfund_amount = rule_line.amount
                        
            total_adj_rule_count += 1
            for ora_tax in ora_tax_opening:
                if total_adj_rule_count == (total_rule_count-1):
                    total_amount += ora_tax.taxable_amount
                if total_adj_rule_count == total_rule_count:
                    total_amount += ora_tax.tax_ded_amount    
            total_amount_list.append({
                'amount': round(total_amount)
            })   
        ppfund_amount=0
        
        
        taxable_amount_adj = self.env['taxable.ded.entry'].search([('employee_id','=',employee.id),('date','>=',date_from ),('date','<=',date_to)])
        for line_adj in taxable_amount_adj:
            tax_rebate_detail.append({
              'name':   str(line_adj.remarks if line_adj.remarks else ' Taxable Amount Adjutment '),
              'period': line_adj.date.strftime('%b-%y'),
              'amount_credit':  line_adj.amount,
              'tax_credit':   0,
              'loan_amount':  0,
            })
         
        tax_credit=self.env['hr.tax.credit'].search([('employee_id','=', employee.id),('date','>=', date_from),('date','<=', date_to)])
        if tax_credit:
            for tax_line in tax_credit:
                tax_rebate_detail.append({
                  'name':   str(tax_line.credit_type_id.name)+'  '+str(tax_line.remarks),
                  'period': tax_line.date.strftime('%b-%y'),
                  'amount_credit':  0,
                  'tax_credit':   tax_line.tax_amount,
                  'loan_amount':  0,
                })
            
        tax_range=self.env['hr.tax.range.line'].search([('year','=',date_to.year)])
        exceed_limit = False
        pfund_amount=0
        if tax_range: 
            pf=0              
            apf=0 
            if employee.pf_member in ('yes_with', 'yes_without'): 
                pf=((contract.wage * employee.company_id.pf_percent)/100) * 12 
            if  employee.pf_effec_date:  
                if employee.pf_effec_date > date_from and employee.pf_effec_date < date_to :
                    current_month_pf_amt = 0
                    month_days = self.env['fiscal.year.month'].sudo().search([('id','=',employee.pf_effec_date.month)], limit=1).days
                    month_start_date = employee.pf_effec_date.replace(day=1)
                    month_end_date = employee.pf_effec_date.replace(day=month_days)
                    fiscal_month = employee.pf_effec_date.month
                    if employee.pf_effec_date:
                        if  employee.pf_effec_date > month_start_date and employee.pf_effec_date < month_end_date:
                            pf=((contract.wage * employee.company_id.pf_percent)/100) * fiscal_month  
                            total_pf_amt = (((contract.wage * employee.company_id.pf_percent)/100))/month_days
                            delta_days = (month_end_date - employee.pf_effec_date).days 
                            current_month_pf_amt = total_pf_amt * delta_days
                            pf = pf + current_month_pf_amt
            apf = 0
            if pf > employee.company_id.pf_exceeding_amt:
                apf=pf-employee.company_id.pf_exceeding_amt    
            if(pf>150000):
                pfund_amount=pf-150000
                exceed_limit = True 
                
            return {
                'docs': docs,
                'date_from': date_from,
                'date_to':  date_to,
                'employee': employee,
                'ora_tax_opening': ora_tax_opening,
                'payslips': payslips,
                'exceed_limit': exceed_limit,
                'pfund_amount': pfund_amount,
                'salary_rules': salary_rules,
                'total_amount_list': total_amount_list,
                'tax_rebate_detail': tax_rebate_detail,
                'tax_range': tax_range,
            }
        else:
            raise UserError("There is not any Payslips in between selected dates")