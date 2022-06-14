import json
from odoo import models
from odoo.exceptions import UserError

class EOBIContributionReport(models.AbstractModel):
    _name = 'report.de_employee_reports.eobi_report'
    _description = 'EOBI Report'
    
    
    
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        eobi_list = []
        eobi_list = self.env['hr.payslip'].search([('fiscal_month','=', docs.date.month),('tax_year','=', docs.date.year),('company_id','=',docs.company_id.id)])
        if docs.location_ids:
            eobi_list = self.env['hr.payslip'].search([('employee_id.work_location_id', 'in', docs.location_ids),('fiscal_month','=', docs.date.month),('tax_year','=', docs.date.year),('company_id','=',docs.company_id.id)])
        return {
                'docs': docs,
                'eobi_list': eobi_list,
        }
    
    
    