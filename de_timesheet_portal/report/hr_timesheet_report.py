# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
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

class HrTimesheetReport(models.AbstractModel):
    _name = 'report.de_timesheet_portal.timesheet_report'
    _description = 'Timesheet Report'
    
    
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env['timesheet.report.wizard'].browse(self.env.context.get('active_id'))
        employees = docs.employee_ids
        type = docs.type
        date_from = docs.start_date
        date_to =  docs.end_date
        req_date_from = docs.start_date
        req_date_to = docs.end_date
        if not docs.employee_ids:
            employees = data['employee']
            type = data['ora_type']
            date_from = data['start_date']
            date_to =  data['end_date'] 
            req_date_from = datetime.strptime(str(data['start_date']), "%Y-%m-%d")
            req_date_to = datetime.strptime(str(data['end_date']), "%Y-%m-%d")
        ora_type = type   
        for employee in employees:
            detail_timesheet_data = []
            summary_timesheet_data =[]
            timesheet_data = []
            tot_planned_hrs = 0
            tot_worked_hrs = 0
            tot_idle_hrs = 0
            
            timesheet_lines=self.env['account.analytic.line'].sudo().search([('employee_id','=',employee.id),('line_date','>=',date_from),('line_date','<=',date_to),('sheet_id.state','!=','refused')], order='line_date ASC')
            #if type=='summary':
            days = (req_date_to - req_date_from).days
            start_date = req_date_from
            rest_day = '0'
            general_shift = self.env['resource.calendar'].sudo().search([('shift_type','=','general')], limit=1)
            for day in range(days+1):
                rest_day = '0'
                start_date = req_date_from + timedelta(day) 
                day_total_worked_hrs = 0
                daytime=self.env['account.analytic.line'].sudo().search([('employee_id','=',employee.id),('line_date','=',start_date),('sheet_id.state','!=','refused')])
                for ora_time in daytime:
                    day_total_worked_hrs += ora_time.unit_amount
                shift_planned_hrs = 0
                shift_schedule_line = self.env['hr.shift.schedule.line'].sudo().search([('employee_id','=',employee.id),('date','=',start_date),('state','=','posted')], limit=1)
                if not shift_schedule_line:
                    shift_planned_hrs += general_shift.hours_per_day
                if not shift_schedule_line.rest_day==True:    
                    shift_planned_hrs += shift_schedule_line.first_shift_id.hours_per_day
                    general_shift = shift_schedule_line.first_shift_id
                    if shift_schedule_line.second_shift_id:
                        shift_planned_hrs += shift_schedule_line.second_shift_id.hours_per_day

                if shift_schedule_line.rest_day==True:
                   rest_day='1' 
                for gazetted_day in general_shift.global_leave_ids:
                    gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                    gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                    if str(start_date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(start_date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')): 
                        rest_day = '1'        
                diff_hrs = 0  
                if rest_day=='0':    
                    diff_hrs = shift_planned_hrs - day_total_worked_hrs
                    tot_planned_hrs += shift_planned_hrs
                if diff_hrs < 0:
                    diff_hrs = 0
                if diff_hrs > 0:
                    tot_idle_hrs += diff_hrs
                tot_worked_hrs += day_total_worked_hrs    
                summary_timesheet_data.append({
                    'date': start_date.strftime('%d-%b-%y'),
                    'rest_day': rest_day,
                    'planned_hrs': shift_planned_hrs if rest_day=='0' else  0,
                    'worked_hrs': day_total_worked_hrs,
                    'idle_hrs': diff_hrs,
                })    
            if type=='detail':  
                ora_type = 'detail'
                detail_timesheet_data=timesheet_lines 
                
            timesheet_data.append({
                'employee_no': employee.emp_number ,
                'tot_planned_hrs': tot_planned_hrs,
                'tot_worked_hrs': tot_worked_hrs,
                'tot_idle_hrs': tot_idle_hrs,
                'name': employee.name,
                'date_from': req_date_from.strftime('%d-%b-%y'),
                'date_to': req_date_to.strftime('%d-%b-%y'),
                'department': employee.department_id.name,
                'manager': employee.parent_id.name,
                'summary_timesheet_data': summary_timesheet_data,
                'detail_timesheet_data': timesheet_lines,
            })
        return {
                'docs': docs,
                'type': ora_type,
                'timesheet_data': timesheet_data,
               }