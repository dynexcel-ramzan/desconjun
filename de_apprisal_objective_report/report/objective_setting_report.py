import json
from odoo import models
from odoo.exceptions import UserError


class ApprisalReportXlS(models.AbstractModel):
    _name = 'report.de_apprisal_objective_report.apprisal_report_xlx'
    _description = 'Apprisal objective report'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['hr.appraisal.objective'].browse(self.env.context.get('active_ids'))
        format1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('Apprisal objective report')
        bold = workbook. add_format({'bold': True, 'align': 'center','border': True})
        
        sheet.set_column('A:B', 20,)
        sheet.set_column('C:D', 20,)
        sheet.set_column('E:F', 20,)
        sheet.set_column('G:H', 20,)
        sheet.set_column('I:J', 20,)
        sheet.set_column('K:L', 20,)
        sheet.set_column('M:N', 20,)
        
        sheet.write(1,0, 'Employee Number',bold)
        sheet.write(1,1, 'Employee' ,bold)
        sheet.write(1,2, 'Date Of Joining' ,bold)
        sheet.write(1,3, 'Manager' ,bold)
        sheet.write(1,4, 'HOD' ,bold)
        sheet.write(1,5, 'Employee Status' ,bold)   
        sheet.write(1,6, 'Work location' ,bold)
        sheet.write(1,7, 'Department' ,bold)
        sheet.write(1,8, 'Objective Year',bold)
        sheet.write(1,9, 'Status',bold)
        sheet.write(1,10, 'Company',bold)
        sheet.write(1,11, 'Grade Type',bold)
        sheet.write(1,12, 'Employee Type',bold)
        sheet.write(1,13, 'Job Position',bold)
        sheet.write(1,14, 'Grade',bold)
        sheet.write(1,15, 'Remarks',bold)
        
        row = 3
        Apprisal_objective = self.env['hr.appraisal.objective'].search([])
        for line in lines: 
            employee_type = line.employee_id.emp_type
            if line.employee_id.emp_type=='permanent':
                employee_type = 'Regular'  
            if line.employee_id.emp_type=='contractor':
                employee_type = 'Contract'
            financial_year = 'FY-2021-22' 
            if line.create_date:
                financial_year = 'FY-'+str(int(line.create_date.strftime('%y'))-1)+' '+str(line.create_date.strftime('%y')) 
            STATUS='Draft' 
            if line.state=='draft':
                STATUS='Draft'
            if line.state=='waiting':
                STATUS='Manager Approval Pending'
            if line.state=='confirm':
                STATUS='Confirmed'         
            sheet.write(row, 0, line.emploee_code, format1)
            sheet.write(row, 1, line.employee_id.name, format1)
            sheet.write(row, 2, line.employee_id.date.strftime('%d-%b-%Y') if line.employee_id.date else '-', format1) 
            sheet.write(row, 3, line.employee_id.parent_id.name, format1)
            sheet.write(row, 4, line.employee_id.department_id.manager_id.name if line.employee_id.department_id.manager_id else '-', format1)
            sheet.write(row, 5, 'Active' if line.employee_id.active==True else 'In-Active', format1)
            sheet.write(row, 6, line.department_id.name, format1)
            sheet.write(row, 7, line.work_location_id.name, format1)
            sheet.write(row, 8, str(financial_year), format1)  
            sheet.write(row, 9, str(STATUS), format1)
            sheet.write(row, 10, line.company_id.name, format1) 
            sheet.write(row, 11, line.grade_type_id.name, format1) 
            sheet.write(row, 12,  str(employee_type), format1)  
            sheet.write(row, 13, line.job_id.name, format1)
            sheet.write(row, 14, line.employee_id.grade_designation.name, format1) 
            sheet.write(row, 15, line.description, format1)
            row += 1           