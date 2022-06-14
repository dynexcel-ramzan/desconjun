# -*- coding: utf-8 -*-
import time
from odoo import api, models, _ , fields 
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class PFLedgerReport(models.AbstractModel):
    _name = 'report.de_account_pf_ledger.pf_ledger_report'
    _description = 'PF Ledger Report'
  
    
    def _get_report_values(self, docids, data=None):
        docs = self.env['pf.ledger.wizard'].browse(self.env.context.get('active_id'))
        employee = docs.employee_id.id
        date_from = docs.date_from
        date_to = docs.date_to
        if not docs.employee_id:
            employee = data['employee']
            date_from = datetime.strptime(str(data['start_date']), "%Y-%m-%d")
            date_to = datetime.strptime(str(data['end_date']), "%Y-%m-%d")  
            
        active_employee = self.env['hr.employee'].search([('id','=',employee)], limit=1)    
        pf_ledger = self.env['partner.pf.ledger'].search([('employee_id','=', employee),('date','>=', date_from),('date','<=',date_to)], order='date ASC')
        opening_balance_list = []
        opening_balance_ledger = self.env['partner.pf.ledger'].search([('employee_id','=', employee),('date','<', date_from)], order='date ASC')
        total_opening_balance = 0
        total_opening_credit = 0
        total_opening_debit = 0
        opening_balance_list = []
        for open_line in opening_balance_ledger:
            total_opening_balance +=  abs(open_line.balance)  
            total_opening_credit += abs(open_line.credit)
            total_opening_debit += abs(open_line.debit)
            
        pf_type_list=[]
        total_pf_type_list=[ ]
        if total_opening_balance > 0:
            line_vals = {
                'name': 'Opening Balance',
                'debit': total_opening_debit,
                'credit': total_opening_credit,
                'balance': total_opening_debit- total_opening_credit,
            }
            total_pf_type_list.append(line_vals)
            opening_balance_list.append(line_vals)
            
        for pf_line in pf_ledger:
            if pf_line.type_id:
                pf_type_list.append(pf_line.type_id.id)
            
        uniq_pf_type_list = set(pf_type_list)
        final_pf_ledger_list = self.env['pf.ledger.type'].search([('id','in',list(uniq_pf_type_list))], order='sequence ASC')   
        for uniq_type in final_pf_ledger_list:
            total_debit = 0
            total_credit = 0
            total_balance = 0
            uniq_pf_ledger = self.env['partner.pf.ledger'].search([('type_id','=',uniq_type.id),('employee_id','=', employee),('date','>=', date_from),('date','<=',date_to)], order='date ASC')
            for uniq_pf in uniq_pf_ledger:
                total_debit += abs(uniq_pf.debit)
                total_credit += abs(uniq_pf.credit)
                total_balance += abs(uniq_pf.balance)
            type_desc = self.env['pf.ledger.type'].search([('id','=',uniq_type.id)], limit=1)
            line_vals = {
                'name': type_desc.name,
                'debit': total_debit,
                'credit': total_credit,
                'balance': total_debit - total_credit,
            }
            total_pf_type_list.append(line_vals)
        return {
                'docs': docs,
                'total_pf_type_list': total_pf_type_list,
                'active_employee': active_employee,
                'opening_balance_list': opening_balance_list,
                'pf_ledger': pf_ledger,
                'date_from': date_from,
                'date_to': date_to,
               }