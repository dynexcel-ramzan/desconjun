# -*- coding: utf-8 -*-

import json
from odoo import models
from odoo.exceptions import UserError


class BatchBankPayslip(models.Model):
    _name = 'report.de_payroll_batch_report_xlsx.batch_bank_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        format1 = workbook.add_format({'font_size': '12', 'align': 'left', 'bold': True})
        format_right = workbook.add_format({'font_size': '12', 'align': 'right'})
        format_left = workbook.add_format({'font_size': '12', 'align': 'left'})
        format_total = workbook.add_format({'font_size': '12', 'align': 'right', 'bold': True,'border': True})
        sheet1 = workbook.add_worksheet('Bank Details')
        bold = workbook. add_format({'bold': True, 'align': 'center','border': True})
        sr_no = 1
        row = 1
        sheet1.write(0, 0, 'Branch', format1)
        sheet1.write(0, 1, 'Account Type', format1)
        sheet1.write(0, 2, 'Customer Number', format1)
        sheet1.write(0, 3, 'Run Number', format1)
        sheet1.write(0, 4, 'Check Digit', format1)
        sheet1.write(0, 5, 'Amount', format1)
        sheet1.set_column(0, 1, 10)
        sheet1.set_column(2, 2, 15)
        sheet1.set_column(3, 3, 10)
        sheet1.set_column(4, 4, 10)
        sheet1.set_column(5, 5, 20)
        total_net_payable = 0
        payslips=self.env['hr.payslip'].search([('payslip_run_id','=',lines.id),('state','!=','cancel')])
        extra_payroll_rule= self.env['hr.salary.rule'].search([('detail_report','=',True),('detail_deduction','!=',True),('detail_compansation','!=',True)], order='detail_sequence asc')

        deduction_rule= self.env['hr.salary.rule'].search([('detail_deduction','=',True)], order='detail_sequence asc')
        compansation_rule= self.env['hr.salary.rule'].search([('detail_compansation','=',True)], order='detail_sequence asc')
        deduction_rule_list=[]
        compansation_rule_list=[]
        extra_rule_list=[]
        
        for extra_rule in extra_payroll_rule:
            extra_rule_amount=0
            for extra_slip in payslips:
                for extra_slip_rule in extra_slip.line_ids:
                    if extra_slip_rule.salary_rule_id.id==extra_rule.id:
                        extra_rule_amount +=   extra_slip_rule.amount  
                        
            if extra_rule_amount !=0:
                extra_rule_list.append(extra_rule.id)
        
        for comp_rule in compansation_rule:
            comp_rule_amount=0
            for compansation_slip in payslips:
                for compansation_rule in compansation_slip.line_ids:
                    if compansation_rule.salary_rule_id.id==comp_rule.id:
                        comp_rule_amount +=   compansation_rule.amount  
                        
            if comp_rule_amount !=0:
                compansation_rule_list.append(comp_rule.id)
                
        for ded_rule in deduction_rule:
            ded_rule_amount=0
            for ded_slip in payslips:
                for deduction_rule in ded_slip.line_ids:
                    if deduction_rule.salary_rule_id.id==ded_rule.id:
                        ded_rule_amount +=   deduction_rule.amount  
                        
            if ded_rule_amount !=0:
                deduction_rule_list.append(ded_rule.id)  
         
        uniq_compansation_rule_list = set(compansation_rule_list)   
        uniq_deduction_rule_list = set(deduction_rule_list) 
        uniq_extra_rule_list = set(extra_rule_list) 
        uniq_deduction_rule= self.env['hr.salary.rule'].search([('id','in',list(uniq_deduction_rule_list))], order='detail_sequence asc')
        uniq_compansation_rule= self.env['hr.salary.rule'].search([('id','in',list(uniq_compansation_rule_list))], order='detail_sequence asc')
        uniq_extra_rule= self.env['hr.salary.rule'].search([('id','in',list(uniq_extra_rule_list))], order='detail_sequence asc')
            
        for slip in payslips:
            net_payable = 0
            for rule_line in slip.line_ids:
                if rule_line.code=='NET':
                    net_payable = rule_line.amount 
            account_split = slip.employee_id.bank_account_id.acc_number.split('-')
            col_no = 0 
            for acc_splt in account_split: 
                sheet1.write(row, col_no, str(acc_splt), format_right)
                sheet1.write(row, col_no, str(acc_splt), format_right)
                sheet1.write(row, col_no, str(acc_splt), format_left)
                sheet1.write(row, col_no, str(acc_splt), format_right)
                col_no += 1 
            sheet1.write(row, col_no, str('{0:,}'.format(int(round(net_payable)))), format_right)
            total_net_payable +=round(net_payable)
            row +=1

        row += 1
        col_no = 0  
        for acc_splt in account_split:    
            sheet1.write(row, col_no, ' ', format_right)
            sheet1.write(row, col_no, ' ', format_right)
            sheet1.write(row, col_no, ' ', format_left)
            sheet1.write(row, col_no, ' ', format_right)
            col_no += 1
        sheet1.write(row, col_no, str('{0:,}'.format(int(round(total_net_payable)))), format_total) 
        
        