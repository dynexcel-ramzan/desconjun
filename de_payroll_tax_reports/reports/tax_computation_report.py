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

        payslips=self.env['hr.payslip'].sudo().search([('employee_id','=',employee.id),('date_to','>=',date_from),('date_to','<=',date_to),('tax_year','>','2021'),('state','!=','cancel') ], order='date_to asc')
        salary_rules=self.env['hr.salary.rule'].sudo().search([('computation_report','=',True)], order='computation_sequence asc')
        
        ora_tax_opening = self.env['hr.tax.ded'].sudo().search([('employee_id','=',employee.id),('date','>=',date_from),('date','<=',date_to),('period_num','<', 8),('tax_year','in', ('2021','2022')) ], order='date asc')
        
        pfund_rule=self.env['hr.salary.rule'].sudo().search([('pfund_amount','=',True)], limit=1) 
        contract=self.env['hr.contract'].sudo().search([('employee_id','=',employee.id),('state','=','open')], limit=1)
        
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
            previous_pf_amount=0
            latest_payslip = self.env['hr.payslip'].sudo().search([('employee_id','=',employee.id)], order='date_to DESC', limit=1)
            current_year_vals=int(latest_payslip.date_to.year)
            if latest_payslip.date_to.month in (1,2,3,4,5,6):
                previous_year_vals=int(latest_payslip.date_to.year) - 1                
                previous_year_tax_data = self.env['hr.tax.ded'].search([('employee_id','=',employee.id),('period_num','in',(1,2,3,4,5,6)),('tax_year','=', previous_year_vals )]) 
                for prv_year_tax in previous_year_tax_data:
                    previous_pf_amount += prv_year_tax.pf_amount                
            current_year_tax_data = self.env['hr.tax.ded'].search([('employee_id','=',employee.id),('period_num','in', (1,2,3,4,5,6,7,8,9,10,11,12)),('tax_year','=', current_year_vals),('fiscal_month','<',latest_payslip.date_to.month) ], order='period_num asc')
            for curr_year_tax in current_year_tax_data:
                previous_pf_amount += curr_year_tax.pf_amount

            curr_year_month_fiscal_month = latest_payslip.date_to.month
            month_passed = 0
            if curr_year_month_fiscal_month==8:
                month_passed = 1
            elif curr_year_month_fiscal_month==9:
                month_passed = 2
            elif curr_year_month_fiscal_month==10:
                month_passed = 3
            elif curr_year_month_fiscal_month==11:
                month_passed = 4
            elif curr_year_month_fiscal_month==12:
                month_passed = 5
            elif curr_year_month_fiscal_month==1:
                month_passed = 6
            elif curr_year_month_fiscal_month==2:
                month_passed = 7
            elif curr_year_month_fiscal_month==3:
                month_passed = 8
            elif curr_year_month_fiscal_month==4:
                month_passed = 9
            elif curr_year_month_fiscal_month==5:
                month_passed = 10
            elif curr_year_month_fiscal_month==6:
                month_passed = 11

            fiscal_month = 12 - (month_passed)
            if employee.pf_member in ('yes_with', 'yes_without'): 
                pf=previous_pf_amount + ((contract.wage * employee.company_id.pf_percent)/100) * fiscal_month
            if  employee.pf_effec_date:  
                if str(employee.pf_effec_date) > date_from.strftime('%Y-%m-%d') and str(employee.pf_effec_date) < date_to.strftime('%Y-%m-%d') :
                    current_month_pf_amt = 0
                    month_days = self.env['fiscal.year.month'].sudo().search([('id','=',employee.pf_effec_date.month)], limit=1).days
                    month_start_date = employee.pf_effec_date.replace(day=1)
                    month_end_date = employee.pf_effec_date.replace(day=month_days)
                    
                    remaining_fiscal_month = 0
                    tax_fiscal_month = employee.pf_effec_date.month
                    if tax_fiscal_month==7:
                        remaining_fiscal_month = 11
                    elif tax_fiscal_month==8:
                        remaining_fiscal_month = 10
                    elif tax_fiscal_month==9:
                        remaining_fiscal_month = 9
                    elif tax_fiscal_month==10:
                        remaining_fiscal_month = 8
                    elif tax_fiscal_month==11:
                        remaining_fiscal_month = 7
                    elif tax_fiscal_month==12:
                        remaining_fiscal_month = 6
                    elif tax_fiscal_month==1:
                        remaining_fiscal_month = 5
                    elif tax_fiscal_month==2:
                        remaining_fiscal_month = 4
                    elif tax_fiscal_month==3:
                        remaining_fiscal_month = 3
                    elif tax_fiscal_month==4:
                        remaining_fiscal_month = 2
                    elif tax_fiscal_month==5:
                        remaining_fiscal_month = 1
                    elif tax_fiscal_month==6:
                        remaining_fiscal_month = 0 
                    if employee.pf_effec_date:
                        if  employee.pf_effec_date > month_start_date and employee.pf_effec_date < month_end_date:
                            pf=((contract.wage * employee.company_id.pf_percent)/100) * remaining_fiscal_month  
                            total_pf_amt = (((contract.wage * employee.company_id.pf_percent)/100))/month_days
                            delta_days = (month_end_date - employee.pf_effec_date).days+1
                            current_month_pf_amt = total_pf_amt * delta_days
                            pf = pf + current_month_pf_amt
            apf = 0
            if pf > employee.company_id.pf_exceeding_amt:
                apf=pf - employee.company_id.pf_exceeding_amt    
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