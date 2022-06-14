# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import cx_Oracle

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    
    oracle_posted = fields.Boolean(string='Post To Oracle')    

    def action_post_payroll_data_delete(self):
        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
        cur = conn.cursor()
        statement = "delete from XX_ODOO_GL_INTERFACE where group_id='50422022061387'"
        cur.execute(statement)
        conn.commit()


    def action_post_payroll_data(self):
        if self.oracle_posted==True:
            raise UserError('Already Data posted to Oracle!')
        analytic_account_list = []
        credit_account_list = []
        debit_account_list = []
        final_gl_account_list = []
        move_lines = 0
        journala = 0
        payslip = 0
        ora_date = fields.date.today()
        for line in self:
            ledgerna = line.company_id.ledger_id
            journala = 0
            ora_date = line.date_end
            payslip = self.env['hr.payslip'].search([('move_id', '=', line.id)], limit=1)
            move_lines = self.env['account.move.line'].search(
                [('company_id', '=', self.company_id.id), ('date', '>=', self.date_end),('date','<=',self.date_end),('journal_id.ora_ledger_label','=','Payroll'),('move_id.state' , '=' , 'posted')])
        for mv in move_lines:
            ledgerna = mv.move_id.company_id.ledger_id
            ora_date = mv.date
            journala = mv.move_id.journal_id.id 
            if mv.account_id.ora_credit==True:  
                credit_account_list.append(mv.account_id.id)
            if mv.account_id.ora_debit==True:  
                debit_account_list.append(mv.account_id.id)                
            analytic_account_list.append(mv.analytic_account_id.id) 
                
        uniq_analytic_account_list = set(analytic_account_list)
        uniq_credit_account_list = set(credit_account_list)
        uniq_debit_account_list = set(debit_account_list)
        mv_account_code = 0
        for credit_account in uniq_credit_account_list:
            credit_total = 0
            mv_account_code = 0
            company = 0
            for mv_line in move_lines:
                if credit_account == mv_line.account_id.id:
                    credit_total +=  mv_line.credit
                    company = mv_line.move_id.company_id.id
            if  credit_total > 0:  
                ora_credit_account = self.env['account.account'].search([('id','=', credit_account)], limit=1)    
                code_spliting = ora_credit_account.code.split('.')      
                ora_ledger = self.env['ora.ledger.report'].create({
                        'company_id':  company, 
                        'journal_id': journala,
                        'payslip_run_id': self.id,                      
                        'account_id': credit_account, 
                        'control_account_id': self.env['controlled.account'].search([('code','=',code_spliting[0] )]).id , 
                        'date':  ora_date,
                        'debit':  0,
                        'credit': credit_total,
                })
                ora_ledger.action_posted_on_oracle_payroll()
        debit_mv_account_code = 0        
        for analytic in uniq_analytic_account_list:            
            for debit_account in uniq_debit_account_list:
                debit_total = 0 
                debit_mv_account_code = 0
                for mv_line in move_lines:
                    if analytic == mv_line.analytic_account_id.id and debit_account == mv_line.account_id.id:
                        debit_total +=  mv_line.debit
                        debit_mv_account_code = mv_line.ora_account_code
                if  debit_total > 0: 
                    ora_debit_account = self.env['account.account'].search([('id','=', debit_account)], limit=1)    
                    code_spliting = ora_debit_account.code.split('.')   
                    ora_ledger = self.env['ora.ledger.report'].create({
                        'company_id':  company, 
                        'journal_id': journala, 
                        'payslip_run_id': self.id,  
                        'analytic_account_id':  analytic,                        
                        'account_id': debit_account, 
                        'control_account_id': self.env['controlled.account'].search([('code','=',code_spliting[0])], limit=1).id , 
                        'date':  ora_date,
                        'debit':  debit_total,
                        'credit': 0,
                    }) 
                    ora_ledger.action_posted_on_oracle_payroll()
        self.oracle_posted=True   


class Hr(models.Model):
    _inherit = 'hr.payslip'

    
    def action_generate_entry(self):
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        for payslip in self:
            contract=self.env['hr.contract'].search([('employee_id','=',payslip.employee_id.id),('state','=','open')], limit=1)
            if not contract:
                contract=self.env['hr.contract'].search([('employee_id','=',payslip.employee_id.id)], limit=1)  
            cost_center_check_percent = 0
            for cost_center in contract.cost_center_information_line:
                cost_center_check_percent += cost_center.percentage_charged 
                if not cost_center.controlled_id:
                    raise UserError('Control-Account Not Set properly on employee Contract! '+str(payslip.employee_id.name)+'-'+str(payslip.employee_id.emp_number))    
            if cost_center_check_percent > 100 or cost_center_check_percent < 100: 
                raise UserError('Cost Center Percentage Distribution Not Correct for Employee! '+str(payslip.employee_id.name)+'-'+str(payslip.employee_id.emp_number) )
            move_dict = {
                  #'name': payslip.name,
                  'journal_id': payslip.journal_id.id,
                  'date': payslip.date_to,
                  'partner_id': payslip.employee_id.address_home_id.id,
                  'state': 'draft',
                       }
                            #step2:debit side entry
            for rule in payslip.line_ids:
                if rule.amount !=0:
                    for cost_center in contract.cost_center_information_line:
                        if cost_center.percentage_charged > 0:
                            credit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('controlled_id','=',cost_center.controlled_id.id),('company_id','=', payslip.employee_id.company_id.id),('ora_credit','=',True)], limit=1)
                            if not credit_account:
                                credit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('company_id','=', payslip.employee_id.company_id.id),('ora_credit','=',True)], limit=1)

                            if credit_account:
                                #if account.ora_credit== True:
                                credit_line = (0, 0, {
                                        'name': rule.name,
                                        'ora_account_code':  str(payslip.employee_id.company_id.segment1)+'.000.'+str(credit_account.code)+'.'+str(payslip.employee_id.work_location_id.location_code if payslip.employee_id.work_location_id.location_code else '00')+'.00',
                                        'partner_id': payslip.employee_id.address_home_id.id,
                                        'debit': 0.0,
                                        'credit': abs((rule.amount/100)* cost_center.percentage_charged),
    #                                     'analytic_account_id': cost_center.cost_center.id,
                                        'account_id': credit_account.id,
                                             })
                                line_ids.append(credit_line)
                                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
                            debit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('controlled_id','=',cost_center.controlled_id.id),('company_id','=', payslip.employee_id.company_id.id),('ora_debit','=',True),('emp_type','=',payslip.employee_id.emp_type),('grade_type_id','=',payslip.employee_id.grade_type.id)], limit=1)
                            
                            if not debit_account:
                                debit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('controlled_id','=',cost_center.controlled_id.id),('company_id','=', payslip.employee_id.company_id.id),('ora_debit','=',True),('emp_type','=',payslip.employee_id.emp_type)], limit=1)    
                            if not debit_account:
                                debit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('company_id','=', payslip.employee_id.company_id.id),('ora_debit','=',True),('emp_type','=',payslip.employee_id.emp_type),('grade_type_id','=',payslip.employee_id.grade_type.id)], limit=1)
                            if not debit_account:
                                debit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('controlled_id','=',cost_center.controlled_id.id),('company_id','=', payslip.employee_id.company_id.id),('ora_debit','=',True)], limit=1)
                            if not debit_account:
                                debit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('company_id','=', payslip.employee_id.company_id.id),('ora_debit','=',True)], limit=1)
                            if debit_account:
                                extra_deduct_amount = 0   
                                if rule.salary_rule_id.ora_extra_from_ded==True:
                                    for e_rule in payslip.line_ids:
                                        if e_rule.salary_rule_id.ora_extra_to_ded==True:
                                            extra_deduct_amount += e_rule.amount
                                debit_line = (0, 0, {
                                        'name': rule.name,
                                        'ora_account_code':  str(payslip.employee_id.company_id.segment1)+'.'+str(cost_center.cost_center.code)+'.'+str(debit_account.code)+'.'+str(payslip.employee_id.work_location_id.location_code if payslip.employee_id.work_location_id.location_code else '00')+'.00',
                                        'partner_id': payslip.employee_id.address_home_id.id,
                                        'debit': abs(((rule.amount/100)* cost_center.percentage_charged)-((extra_deduct_amount/100)*cost_center.percentage_charged)),
                                        'credit': 0.0,
                                        'analytic_account_id': cost_center.cost_center.id,
                                        'account_id': debit_account.id,
                                             })
                                line_ids.append(debit_line)
                                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            account=self.env['account.account'].search([], limit=1)
           
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            payslip.update({
                'move_id': move.id,
            })

    
    
    
    
