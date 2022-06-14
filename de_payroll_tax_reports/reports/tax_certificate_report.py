# -*- coding: utf-8 -*-
#################################################################################
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Dynexcel <www.dynexcel.com>

#################################################################################
import time
from odoo import api, models, fields, _
from dateutil.parser import parse
from odoo.exceptions import UserError

class PayrollTaxComputation(models.AbstractModel):
    _name = 'report.de_payroll_tax_reports.certificate_report'
    _description = 'Tax certificate Report'

    '''Find payroll Tax certificate Report between the date'''
    @api.model
    def _get_report_values(self, docids, data=None): 
        docs = self.env['tax.certificate.wizard'].browse(self.env.context.get('active_id'))
        certificate_list = []
        gross_total = 0
        ora_tax_opening = self.env['hr.tax.ded'].sudo().search([('employee_id','=',docs.employee_id.id),('date','>=',docs.date_from),('date','<=',docs.date_to)], order='date asc')
        payslips=self.env['hr.payslip'].search([('employee_id','=',docs.employee_id.id),('date_to','>=',docs.date_from),('date_to','<=',docs.date_to),('tax_year','>','2021'),('state','!=','cancel')])
        for ora_gross_sum in ora_tax_opening:
            gross_total += ora_gross_sum.taxable_amount    
        detail_bank=docs.bank
        detail_branch=docs.branch
        for line in docs.certificate_line_ids:
            certificate_list.append({
                'period': line.period,
                'bank': line.bank,
                'branch': line.branch,
                'amount': line.amount,
            })    
        return {
                'docs': docs,
                'detail_bank': detail_bank,
                'detail_branch': detail_branch, 
                'issue_date': fields.date.today(),
                'certificate_list': certificate_list,
                'gross_total': gross_total,
            }
       