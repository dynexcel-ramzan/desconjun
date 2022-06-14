from odoo import api, fields, models, _
from calendar import monthrange

from odoo.exceptions import UserError
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta


class HrOvertimeRequest(models.Model):
    _inherit = 'hr.overtime.request'
    
    
    def action_send_approval(self):
        location_list = []
        employee_list = []
        forcast_list = []
        for rec in self:
            forcast_list=rec.employee_id
            location_list.append(rec.employee_id.work_location_id.id)
            
        total_days = forcast_list.company_id.from_date + forcast_list.company_id.to_date
        today_date = fields.date.today()
        month_date_fromcurr = fields.date.today() - timedelta(today_date.day) 
        replmonth_date_from = month_date_fromcurr - timedelta(1)
        month_date_from = replmonth_date_from.replace(day=1)
        date_from = month_date_from - timedelta(1)  + timedelta(forcast_list.company_id.from_date) 
        to_date = date_from- timedelta(1) + timedelta(total_days)
        
        uniq_location_list = set(location_list)
        for uniq_list in uniq_location_list:
            subordinates_overtime_list = []
            employee_list = self.env['hr.employee'].search([('work_location_id','=', uniq_list)])
            for emp in employee_list:
                draft_overtime_reconcile=self.env['hr.overtime.request'].sudo().search([('employee_id','=',emp.id),('date','>=',date_from ),('date','<=',to_date),('state','=','draft')])
                if draft_overtime_reconcile:
                    raise UserError('Their are some Overtime Request which are available in Draft state for this Location. '+str(emp.work_location_id.name)+' Before Sending Approval, Please submit or Cancel It.') 
                empexist = self.env['hr.employee'].search([('id','=',emp.id)], limit=1) 
                loc = self.env['hr.work.location'].search([('id','=',uniq_list)], limit=1)
                normal_overtime_total = 0
                rest_overtime_total = 0
                gazetted_overtime_total=0
                evertime_type_list = []
                overtime_reconcile=self.env['hr.overtime.request'].sudo().search([('employee_id','=',emp.id),('date','>=',date_from ),('date','<=',to_date),('state','=','to_approve')])
                for ovt in overtime_reconcile:
                    if ovt.overtime_hours > 4 and ovt.remarks=='':
                        raise UserError('Please Enter remarks for all Overtime Request which have Feeded Hours more than 4 Hours!')
                    evertime_type_list.append(ovt.overtime_type_id.id) 
                uniq_overtime_type_list = set(evertime_type_list) 
                for uniq_ovt in uniq_overtime_type_list:
                    total_ot_hours = 0
                    overtime_entry_list=self.env['hr.overtime.request'].sudo().search([('employee_id','=',emp.id),('date','>=',date_from ),('date','<=',to_date),('overtime_type_id','=',uniq_ovt),('state','=','to_approve')])  
                    for ot in overtime_entry_list:
                        if ot.overtime_type_id.type=='normal':
                            normal_overtime_total += ot.overtime_hours
                        if ot.overtime_type_id.type=='rest_day':
                            rest_overtime_total += ot.overtime_hours
                        if ot.overtime_type_id.type=='gazetted':
                            gazetted_overtime_total += ot.overtime_hours
                        ot.update({
                              'state':  'approved',
                        }) 
                if  normal_overtime_total > 0 or rest_overtime_total > 0 or gazetted_overtime_total > 0:    
                    subordinates_overtime_list.append({
                      'employee':  emp.id,
                      'normal_overtime': normal_overtime_total,
                      'rest_day_overtime': rest_overtime_total,
                      'gazetted_overtime': gazetted_overtime_total,
                    })        
            overtime_vals={
                'incharge_id': loc.ot_approver_id.id,
                'date_from': date_from,
                'date_to': to_date,
                'work_location_id': loc.id,
                'workf_location_id': loc.id,
                'state': 'draft',
            }  
            ot_approval=self.env['hr.overtime.approval'].sudo().create(overtime_vals)
            for line in subordinates_overtime_list:
                line_vals = {
                          'employee_id': line['employee'],
                          'site_ot_id':  ot_approval.id,
                          'normal_ot':  line['normal_overtime'],
                          'rest_day_ot': line['rest_day_overtime'],
                          'gazetted_ot':  line['gazetted_overtime'],
                }
                overtime_line=self.env['hr.overtime.approval.line'].create(line_vals)    
            ot_approval.update({
               'state': 'submitted',
            })  
  
    

   

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    