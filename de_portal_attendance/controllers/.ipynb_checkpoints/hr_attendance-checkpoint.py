# -*- coding: utf-8 -*-
from . import config
from . import update
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import OrderedDict
from datetime import date, datetime, timedelta
from operator import itemgetter
from datetime import datetime , date
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR
import base64
import ast

def attendance_page_content(flag = 0):
    emps = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    managers = emps.line_manager
    employee_name = emps
    return {
        'emps': emps,
        'managers': managers,
        'employee_name': employee_name,
        'success_flag' : flag,
    }


def print_page_content(flag = 0):
    emps = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    managers = emps.line_manager
    employee_name = emps
    return {
        'emps': emps,
        'managers': managers,
        'employee_name': employee_name,
        'success_flag' : flag,
    }



def paging(data, flag1 = 0, flag2 = 0):        
    if flag1 == 1:
        return config.list12
    elif flag2 == 1:
        config.list12.clear()
    else:
        k = []
        for rec in data:
            for ids in rec:
                config.list12.append(ids.id)  
                
        
class CreateAttendance(http.Controller):
    @http.route('/hr/attendance/rectify/',type="http", website=True, auth='user')
    def approvals_create_template(self, **kw):
        return request.render("de_portal_attendance.attendance_create_rectify", attendance_page_content())


    @http.route('/hr/attendance/print/',type="http", website=True, auth='user')
    def action_print_attendance(self, **kw):
        return request.render("de_portal_attendance.print_attendance_report", print_page_content())
    
   


    @http.route('/hr/attendance/line/save', type="http", auth="public", website=True)
    def action_attendance_user_rectify(self, **kw):
        ora_attendance_vals_list = []
        if kw.get('ora_attendance_vals'):
            ora_attendance_vals_list = ast.literal_eval(kw.get('ora_attendance_vals'))
        inner_count = 0
        count = 0
        for ora_att in ora_attendance_vals_list:   
            count += 1
        for ora_att in ora_attendance_vals_list:   
            inner_count += 1
            if inner_count > 1 and inner_count < count:
                current_att = request.env['hr.attendance'].sudo().search([('id' ,'=', int(ora_att['col7']) )], limit=1)
                """
                   Attendance Date Check 
                """
                if str(current_att.att_date - timedelta(1)) > ora_att['col4']: 
                    raise UserError('You are not allow to select Out Date less than '+str(current_att.att_date + timedelta(1)))
                if str(current_att.att_date + timedelta(1)) < ora_att['col4']: 
                    raise UserError('You are not allow to select Out Date Greater than '+str(current_att.att_date + timedelta(1)))    
                if str(current_att.att_date - timedelta(1)) > ora_att['col1']: 
                    raise UserError('You are not allow to select In Date less than '+str(current_att.att_date - timedelta(1)))  
                if str(current_att.att_date + timedelta(1)) < ora_att['col1']: 
                    raise UserError('You are not allow to select In Date Greater than '+str(current_att.att_date + timedelta(1)))  
                    
                """
                  Attendance Date Updation
                """    
                if ora_att['col1'] != str(current_att.att_date):
                    att_vals = {
                        'check_in': current_att.check_in,
                        'att_date': ora_att['col1'],
                        'is_portal_modify': True,
                        'modify_type':  ora_att['col2'],
                        'in_validity': 'valid' ,
                        'out_validity': 'valid'  ,
                    }
                    att_val=request.env['hr.attendance'].create(att_vals)
                    current_att.update({
                        'check_in': False,
                    })
                if ora_att['col4'] != str(current_att.att_date):
                    att_vals = {
                        'check_in': current_att.check_out,
                        'att_date': ora_att['col4'],
                        'is_portal_modify': True,
                        'modify_type':  ora_att['col5'],
                        'in_validity': 'valid' ,
                        'out_validity': 'valid'  ,
                    }
                    att_val=request.env['hr.attendance'].create(att_vals)
                    current_att.update({
                        'check_out': False,
                    })        
                """
                   Unnecessary Attendance present in odoo
                """
                if ora_att['col3']=='invalid' and ora_att['col6']=='invalid':
                    current_att.update({
                        'in_validity': ora_att['col3']  ,
                        'out_validity': ora_att['col6']  ,
                        'check_in': current_att.check_in,
                        'check_out': current_att.check_out,
                        'att_date': current_att.att_date,
                        'out_date':  ora_att['col4']  ,
                        'in_date':  ora_att['col1']  ,
                        'in_type_validity':  ora_att['col2']  ,
                        'out_type_validity': ora_att['col5']  ,
                    })    
                elif ora_att['col3']=='invalid':
                    if current_att.check_in and current_att.check_out:
                        att_vals = {
                            'check_in': current_att.check_in,
                            'att_date': current_att.check_in,
                            'in_validity': 'invalid'  ,
                            'in_date':  ora_att['col4']  ,
                            'in_type_validity': ora_att['col5']  ,
                        }
                        curr_att=request.env['hr.attendance'].sudo().create(att_vals)
                        current_att.update({
                            'check_in': False,
                        })   
                    elif current_att.check_in:
                        current_att.update({
                            'in_validity': ora_att['col3'],
                            'in_date': ora_att['col1'],
                            'in_type_validity': ora_att['col2'],
                        })
                elif ora_att['col6']=='invalid':
                    if current_att.check_out and current_att.check_in:
                        att_vals = {
                            'check_in': current_att.check_out,
                            'att_date': current_att.check_out,
                            'in_validity': ora_att['col6']  ,
                            'in_date':  ora_att['col4']  ,
                            'in_type_validity': ora_att['col5']  ,
                        }
                        curr_att=request.env['hr.attendance'].create(att_vals)
                        current_att.update({
                            'out_validity': ora_att['col6']  ,
                            'out_date':  ora_att['col4']  ,
                            'out_type_validity': ora_att['col5']  ,
                            'check_out': False,
                        })
                    elif current_att.check_out:
                        current_att.update({
                            'out_validity': ora_att['col6'],
                            'out_date': ora_att['col4'],
                            'out_type_validity': ora_att['col5'],
                        })
                
                """
                   In-valid Attendance present Re-processing
                """
                if ora_att['col3']=='valid' and ora_att['col6']=='valid':
                    current_att.update({
                        'in_validity': ora_att['col3']  ,
                        'out_validity': ora_att['col6']  ,
                        'check_in': current_att.check_in,
                        'check_out': current_att.check_out,
                        'att_date': current_att.att_date,
                        'out_date':  ora_att['col4']  ,
                        'in_date':  ora_att['col1']  ,
                        'in_type_validity':  ora_att['col2']  ,
                        'out_type_validity': ora_att['col5']  ,
                    })    
                elif ora_att['col3']=='valid':
                    if current_att.check_in and current_att.check_out:
                        att_vals = {
                            'check_in': current_att.check_in,
                            'att_date': current_att.check_in,
                            'in_validity': 'valid'  ,
                            'in_date':  ora_att['col4']  ,
                            'in_type_validity': ora_att['col5']  ,
                        }
                        curr_att=request.env['hr.attendance'].sudo().create(att_vals)
                        current_att.update({
                            'in_validity': ora_att['col3']  ,
                            'in_date':  ora_att['col1']  ,
                            'in_type_validity':  ora_att['col2']  ,
                            'check_in': False,
                        })
                    elif current_att.check_in:
                        current_att.update({
                            'in_validity': ora_att['col3'],
                            'in_date': ora_att['col1'],
                            'in_type_validity': ora_att['col2'],
                        })
                elif ora_att['col6']=='valid':
                    if current_att.check_out and current_att.check_in:
                        att_vals = {
                            'check_in': current_att.check_out,
                            'att_date': current_att.check_out,
                            'in_validity': ora_att['col6']  ,
                            'in_date':  ora_att['col4']  ,
                            'in_type_validity': ora_att['col5']  ,
                        }
                        curr_att=request.env['hr.attendance'].sudo().create(att_vals)
                        current_att.update({
                            'out_validity': ora_att['col6']  ,
                            'out_date':  ora_att['col4']  ,
                            'out_type_validity': ora_att['col5']  ,
                            'check_out': False,
                        })
                    elif current_att.check_out:
                        current_att.update({
                            'out_validity': ora_att['col6'],
                            'out_date': ora_att['col4'],
                            'out_type_validity': ora_att['col5'],
                        })
                if ora_att['col2']=='out' and ora_att['col5']=='in':
                    pass
                if ora_att['col2']=='out':
                    att_vals = {
                        'check_in': current_att.check_in,
                        'att_date': ora_att['col1'],
                        'is_portal_modify': True,
                        'modify_type':  ora_att['col2'],
                        'in_validity': 'valid' ,
                        'out_validity': 'valid'  ,
                    }
                    att_val=request.env['hr.attendance'].create(att_vals)
                    current_att.update({
                        'check_in': False,
                    })       
                if ora_att['col5']=='in':
                    att_vals = {
                        'check_in': current_att.check_out,
                        'att_date': ora_att['col4'],
                        'is_portal_modify': True,
                        'modify_type':  ora_att['col5'],
                        'in_validity': 'valid' ,
                        'out_validity': 'valid'  ,
                    }
                    att_val=request.env['hr.attendance'].create(att_vals)
                    current_att.update({
                        'check_out': False,
                    })
                    
        emp_attendance = request.env['hr.attendance'].search([('employee_id.user_id','=', http.request.env.context.get('uid')),('att_date','>=', fields.date.today()-timedelta(30) )  ], order='check_in ASC')
        for emp_att in emp_attendance:
            if emp_att.in_validity=='valid':
                if emp_att.check_in and not emp_att.check_out:
                    today_att=request.env['hr.attendance'].sudo().search([('id','!=',emp_att.id),('employee_id','=',emp_att.employee_id.id),('att_date','=',emp_att.att_date),('out_validity','=','valid'),('check_out','!=',False),('check_in','=', False)], order='check_out DESC',limit=1)
                    today_att_out=request.env['hr.attendance'].sudo().search([('id','!=',emp_att.id),('employee_id','=',emp_att.employee_id.id),('att_date','=',emp_att.att_date),('in_validity','=','valid'),('check_in','!=',False),('check_out','=', False)], order='check_in DESC',limit=1)
                    if today_att:
                        emp_att.update({
                            'check_out': today_att.check_out,
                            'out_validity': 'valid',
                        })
                        today_att.update({
                            'check_out': False,
                        })
                    elif today_att_out:
                        if str(emp_att.check_in) > str(today_att_out.check_in): 
                            emp_att.update({
                                'check_in': today_att_out.check_in,
                                'check_out': emp_att.check_in,
                                'out_validity': 'valid',
                            })
                            today_att_out.update({
                                'check_in': False,
                            })
                        elif str(emp_att.check_in) < str(today_att_out.check_in): 
                            emp_att.update({
                                'check_out': today_att_out.check_in,
                                'out_validity': 'valid',
                            })
                            today_att_out.update({
                                'check_in': False,
                            })    
                    
            if emp_att.out_validity=='valid':
                if not emp_att.check_in and emp_att.check_out:
                    today_att=request.env['hr.attendance'].sudo().search([('id','!=',emp_att.id),('employee_id','=',emp_att.employee_id.id),('att_date','=',emp_att.att_date),('in_validity','=','valid'),('check_out','=', False)], order='check_in ASC',limit=1)
                    emp_att.update({
                        'check_in': today_att.check_in,
                        'out_validity': 'valid',
                    })
                    today_att.update({
                        'check_in': False,
                    })
                    
            if not emp_att.check_in and not emp_att.check_out:
                emp_att.unlink()
                
        return request.redirect('/hr/attendances')
    
    
    #==============================
    
    
    @http.route('/hr/attendance/rectify/save', type="http", auth="public", website=True)
    def create_rectify_attendance(self, **kw):
        checkin_date_in = kw.get('check_in')
        
        if kw.get('date'):
            if kw.get('date') > str(date.today()):
                return request.render("de_portal_attendance.cannot_submit_future_days_commitment_msg", attendance_page_content())
            
        if kw.get('id'):
            exist_attendance1 = request.env['hr.attendance'].search([('id','=',int(kw.get('id')))])
            if not kw.get('check_out'):
                check_out =  exist_attendance1.check_out
                checkin1_date_rectify = check_out.strftime('%Y-%m-%d')
                checkin_date_rectify = datetime.strptime(str(checkin1_date_rectify) , '%Y-%m-%d')
                checkin_duration_obj = datetime.strptime(kw.get('check_in'), '%H:%M')
                checkin_date_in = checkin_date_rectify + timedelta(hours=checkin_duration_obj.hour, minutes=checkin_duration_obj.minute)
                if kw.get('night_shift'):
                    check_out1 = checkin1_date_rectify
                    if checkin1_date_rectify:
                        check_out1 = datetime.strptime(checkin1_date_rectify, '%Y-%m-%d') - timedelta(1)
                    checkin_date_rectify = check_out1
                    checkin_duration_obj = datetime.strptime(kw.get('check_in'), '%H:%M')
                    checkin_date_in = checkin_date_rectify + timedelta(hours=checkin_duration_obj.hour, minutes=checkin_duration_obj.minute)    
                rectify_val = {
                    'reason': kw.get('description'),
                    'employee_id': int(kw.get('employee_id')),
                    'check_in':  checkin_date_in - relativedelta(hours =+ 5),
                    'check_out': check_out,
                    'partial': 'Check In Time Missing',
                    'date':  check_out,
                    'attendance_id':  int(kw.get('id')),
                }
                record = request.env['hr.attendance.rectification'].sudo().create(rectify_val)
                if kw.get('partial'):
                    record.update({
                        'partial': 'Partial',
                    })
                record.action_submit()
                return request.render("de_portal_attendance.rectification_submited", {})
            elif not kw.get('check_in'):
                
                check_in =  exist_attendance1.check_in
                checkout1_date_rectify = check_in.strftime('%Y-%m-%d')
                checkout_date_rectify = datetime.strptime(str(checkout1_date_rectify) , '%Y-%m-%d')
                checkout_duration_obj = datetime.strptime(kw.get('check_out'), '%H:%M')
                checkout_date_in = checkout_date_rectify + timedelta(hours=checkout_duration_obj.hour, minutes=checkout_duration_obj.minute)
                if kw.get('night_shift'):
                    check1_in = checkout1_date_rectify
                    if checkout1_date_rectify:
                        check1_in = datetime.strptime(checkout1_date_rectify, '%Y-%m-%d') + timedelta(1) 
                    checkout_date_rectify = datetime.strptime(str(check1_in) , '%Y-%m-%d %H:%M:%S')
                    checkout_duration_obj = datetime.strptime(kw.get('check_out'), '%H:%M')
                    checkout_date_in = checkout_date_rectify + timedelta(hours=checkout_duration_obj.hour, minutes=checkout_duration_obj.minute)
                
                rectify_val = {
                    'reason': kw.get('description'),
                    'employee_id': int(kw.get('employee_id')),
                    'check_in':  check_in,
                    'check_out': checkout_date_in - relativedelta(hours =+ 5),
                    'date':  check_in,
                    'partial': 'Out Time Missing', 
                    'attendance_id':  int(kw.get('id')),
                }
                record = request.env['hr.attendance.rectification'].sudo().create(rectify_val)
                if kw.get('partial'):
                    record.update({
                        'partial': 'Partial',
                    })
                    
                record.action_submit()
                return request.render("de_portal_attendance.rectification_submited", {})
                
        else:
            if kw.get('partial'):
                if  not kw.get('check_in_time'):
                    raise UserError('Please slect Time In') 
                if  not kw.get('check_out_time'):
                    raise UserError('Please slect Time Out') 
                timein_data = kw.get('check_in_time').split(":")
                check_in_hour = 0
                check_in_minute = 0
                time_count = 0
                for deltatime in timein_data:
                    if time_count == 0:
                        check_in_hour =  deltatime
                    time_count += 1
                    if time_count:
                        check_in_minute =  deltatime  
                timeout_data = kw.get('check_out_time').split(":")
                check_out_hour = 0
                check_out_minute = 0
                time_count = 0
                for deltatime in timeout_data:
                    if time_count == 0:
                        check_out_hour =  deltatime
                    time_count += 1
                    if time_count:
                        check_out_minute =  deltatime          
                timeout_data = float(kw.get('check_in_time').replace(":", "."))
                check_in_datetime = datetime.strptime(kw.get('date_partial'), '%Y-%m-%d') + relativedelta(hours =+ int(check_in_hour), minutes = int(check_in_minute))
                check_out_datetime = datetime.strptime(kw.get('date_partial'),'%Y-%m-%d') + relativedelta(hours =+ int(check_out_hour), minutes = int(check_out_minute))
                
                rectify_val = {
                    'reason': kw.get('description'),
                    'employee_id': int(kw.get('employee_id')),
                    'check_in':  check_in_datetime - relativedelta(hours =+ 5),
                    'check_out': check_out_datetime - relativedelta(hours =+ 5),
                    'partial': 'Partial',
                    'date':  check_in_datetime,
                }
                record = request.env['hr.attendance.rectification'].sudo().create(rectify_val)
                record.action_submit()
                return request.render("de_portal_attendance.rectification_submited", {})
        
            else:
                employee_data = request.env['hr.employee'].sudo().search([('id','=',int(kw.get('employee_id')))], limit=1)
                shift = request.env['resource.calendar'].sudo().search([('shift_type','=', 'general'),('company_id','=',employee_data.company_id.id)], limit=1)
                generate_shift_line = request.env['hr.shift.schedule.line'].sudo().search([('employee_id','=',int(kw.get('employee_id'))),('date','=', kw.get('check_in'))], limit=1)
                if generate_shift_line.first_shift_id:
                    shift =   generate_shift_line.first_shift_id  
                    
                if not shift:
                    employee_data = request.env['hr.employee'].sudo().search([('id','=',int(kw.get('employee_id')))], limit=1)
                    shift = request.env['resource.calendar'].sudo().search([('shift_type','=', 'general'),('company_id','=',employee_data.company_id.id)], limit=1)
                if not shift:    
                    shift = request.env['resource.calendar'].sudo().search([('company_id','=',employee_data.company_id.id)], limit=1)
                hours_from = 8
                hours_to =  16
                
                for shift_line in shift.attendance_ids:
                    hours_from =   shift_line.hour_from     
                    hours_to = shift_line.hour_to 
                attendance_data_in = datetime.strptime(kw.get('check_in'), '%Y-%m-%d') + relativedelta(hours =+ hours_from)
                att_date_out = datetime.strptime(kw.get('check_out'), '%Y-%m-%d') + relativedelta(hours =+ hours_to)
                attendance_data_out =  datetime.strptime(kw.get('check_out'), '%Y-%m-%d') + relativedelta(hours =+ hours_to)
                if shift.shift_type == 'night':
                    delta_diff = datetime.strptime(kw.get('check_out'), '%Y-%m-%d') - datetime.strptime(kw.get('check_in'), '%Y-%m-%d')
                    if delta_diff.days == 0:
                        attendance_data_out =  att_date_out  + timedelta(1)  
                restrict_date = fields.date.today() + timedelta(30)     
                if kw.get('check_in') > str(restrict_date):
                    return request.render("de_portal_attendance.cannot_submit_future_days_commitment_msg", attendance_page_content())
                if kw.get('check_out') > str(restrict_date):
                    return request.render("de_portal_attendance.cannot_submit_future_days_commitment_msg", attendance_page_content())
                rectify_val = {
                    'reason': kw.get('description'),
                    'employee_id': int(kw.get('employee_id')),
                    'check_in':  attendance_data_in - relativedelta(hours =+ 5),
                    'check_out': attendance_data_out - relativedelta(hours =+ 5),
                    'partial': 'Full',
                    'date':  kw.get('check_in'),
                }
                record = request.env['hr.attendance.rectification'].sudo().create(rectify_val)

                if kw.get('partial'):
                    record.update({
                            'partial': 'Partial',
                    })
                record.action_submit()
                return request.render("de_portal_attendance.rectification_submited", {})

    
    @http.route('/attendance/rectify/reverse/save', type="http", auth="public", website=True)
    def reverse_rectify_attendance(self, **kw):
        checkin_date_in = kw.get('check_in')
        
        if kw.get('date'):
            if kw.get('date') > str(date.today()):
                return request.render("de_portal_attendance.cannot_submit_future_days_commitment_msg", attendance_page_content())
            
        if kw.get('id'):
            exist_attendance1 = request.env['hr.attendance'].search([('id','=',int(kw.get('id')))])
            if kw.get('check_out'):
                check_out =  exist_attendance1.check_out
                checkin1_date_rectify = check_out.strftime('%Y-%m-%d')
                checkin_date_rectify = datetime.strptime(str(checkin1_date_rectify) , '%Y-%m-%d')
                checkin_duration_obj = datetime.strptime(kw.get('check_out'), '%H:%M')
                checkin_date_in = checkin_date_rectify + timedelta(hours=checkin_duration_obj.hour, minutes=checkin_duration_obj.minute)
                if kw.get('night_shift'):
                    check_reverse_out1 = checkin1_date_rectify
                    if checkin1_date_rectify:
                        check_reverse_out1 = datetime.strptime(checkin1_date_rectify, '%Y-%m-%d') + timedelta(1)
                    checkin_date_rectify = check_reverse_out1
                    checkin_date_in = checkin_date_rectify + timedelta(hours=checkin_duration_obj.hour, minutes=checkin_duration_obj.minute)
                rectify_val = {
                    'reason': kw.get('description'),
                    'employee_id': int(kw.get('employee_id')),
                    'check_in':  check_out,
                    'check_out': checkin_date_in - relativedelta(hours =+ 5),
                    'partial': 'Out Time Missing',
                    'date':  check_out,
                    'attendance_id':  int(kw.get('id')),
                }
                record = request.env['hr.attendance.rectification'].sudo().create(rectify_val)
                if kw.get('partial'):
                    record.update({
                        'partial': 'Partial',
                    })
                record.action_submit()
                return request.render("de_portal_attendance.rectification_submited", {})
            elif kw.get('check_in'):
                
                check_in =  exist_attendance1.check_in
                checkout1_date_rectify = check_in.strftime('%Y-%m-%d')
                checkout_date_rectify = datetime.strptime(str(checkout1_date_rectify) , '%Y-%m-%d')
                checkout_duration_obj = datetime.strptime(kw.get('check_in'), '%H:%M')
                checkout_date_in = checkout_date_rectify + timedelta(hours=checkout_duration_obj.hour, minutes=checkout_duration_obj.minute)
                if kw.get('night_shift'):
                    check1_in =  datetime.strptime(str(checkout1_date_rectify) , '%Y-%m-%d') - timedelta(1) 
                    checkout_date_rectify = check1_in
                    checkout_duration_obj = datetime.strptime(kw.get('check_in'), '%H:%M')
                    checkout_date_in = checkout_date_rectify + timedelta(hours=checkout_duration_obj.hour, minutes=checkout_duration_obj.minute)
                
                rectify_val = {
                    'reason': kw.get('description'),
                    'employee_id': int(kw.get('employee_id')),
                    'check_in':  checkout_date_in - relativedelta(hours =+ 5),
                    'check_out': check_in,
                    'date':  check_in,
                    'partial': 'Check In Time Missing', 
                    'attendance_id':  int(kw.get('id')),
                }
                record = request.env['hr.attendance.rectification'].sudo().create(rectify_val)
                if kw.get('partial'):
                    record.update({
                        'partial': 'Partial',
                    })
                    
               
       
                record.action_submit()
                return request.render("de_portal_attendance.rectification_submited", {})        

    
    
       
   


class CustomerPortal(CustomerPortal):
    
    def _show_report_portal(self, model, report_type, employee, start_date, end_date, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s", report_type))

        report_sudo = request.env.ref(report_ref).with_user(SUPERUSER_ID)

        if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
            raise UserError(_("%s is not the reference of a report", report_ref))

        if hasattr(model, 'company_id'):
            report_sudo = report_sudo.with_company(model.company_id)

        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(report_sudo, method_name)([model], data={'report_type': report_type,'employee':employee,'start_date':start_date,'end_date':end_date})[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)


    
    @http.route('/hr/attendance/print/report',type="http", website=True,download=False, auth='user')
    def action_print_attendance_report(self, **kw):
        report_type='pdf'
        order_sudo = 'hr.attendance'
        download = False
        employee = request.env['hr.employee'].search([('id','=',int(kw.get('employee_id')))]).id
        start_date = kw.get('check_in')
        end_date = kw.get('check_out')
        return self._show_report_portal(model=order_sudo, report_type=report_type,employee=employee, start_date=start_date, end_date=end_date, report_ref='de_hr_attendance_report.open_hr_report_wizard_action_portal', download=download)
    
    
    @http.route(['/hr/attendance/cancel/<int:attendance_id>'], type='http', auth="public", website=True)
    def action_cancel(self,attendance_id , access_token=None, **kw):
        id=attendance_id
        rectification = request.env['hr.attendance.rectification'].sudo().browse(id)
        approval_rectification = request.env['approval.request'].search([('rectification_id','=',id)])
        
        approval_rectification.action_refuse()
        rectification.action_refuse()
        try:
            rectification_sudo = self._document_check_access('hr.attendance.rectification', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = self._attendance_get_page_view_values(rectification_sudo, **kw) 
        return request.render("de_portal_attendance.rectification_cancel", {})
    
    
    @http.route(['/hr/attendance/rectify/<int:attendance_id>'], type='http', auth="public", website=True)
    def attendance_edit_template(self,attendance_id, access_token=None ,**kw):
        id = attendance_id
        try:
            expense_sudo = self._document_check_access('hr.attendance', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = self._attendance_get_page_view_values(expense_sudo, **kw) 
        exist_attendance = request.env['hr.attendance'].sudo().browse(id)
        employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
        managers = employees.line_manager
        employee_name = employees
        checkin_date_in = str(exist_attendance.check_in)
        date_processing_in = checkin_date_in.replace(':', '-').replace('T', '-').split('-')
        checkout_date_in = str(exist_attendance.check_out) 
        date_processing_out = checkout_date_in.replace(':', '-').replace('T', '-').split('-')
        values.update({
            'exist_attendance': exist_attendance,
            'date_processing_in': date_processing_in,
            'managers': managers,
            'employee_name': employee_name,
            'date_processing_out': date_processing_out,
             'emps' : employees,
        })
        return request.render("de_portal_attendance.attendance_rectify", values)


    @http.route(['/hr/attendance/rectify/reverse/<int:attendance_id>'], type='http', auth="public", website=True)
    def attendance_edit_reverse_template(self,attendance_id, access_token=None ,**kw):
        id = attendance_id
        try:
            expense_sudo = self._document_check_access('hr.attendance', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = self._attendance_get_page_view_values(expense_sudo, **kw) 
        exist_attendance = request.env['hr.attendance'].sudo().browse(id)
        employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
        managers = employees.line_manager
        employee_name = employees
        checkin_date_in = str(exist_attendance.check_in)
        date_processing_in = checkin_date_in.replace(':', '-').replace('T', '-').split('-')
        checkout_date_in = str(exist_attendance.check_out) 
        date_processing_out = checkout_date_in.replace(':', '-').replace('T', '-').split('-')
        values.update({
            'exist_attendance': exist_attendance,
            'date_processing_in': date_processing_in,
            'managers': managers,
            'employee_name': employee_name,
            'date_processing_out': date_processing_out,
             'emps' : employees,
        })
        return request.render("de_portal_attendance.attendance_rectify_reverse", values)
    
    

  
    def _rectify_attendance_get_page_view_values(self,rectify, next_id = 0,pre_id= 0, attendance_user_flag = 0, access_token = None, **kwargs):
        values = {
            'page_name' : 'rectify',
            'rectify' : rectify,
            'attendance_user_flag': attendance_user_flag,
            'next_id' : next_id,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(attendance, access_token, values, 'my_attendance_history', False, **kwargs)

    
    @http.route(['/hr/rectify/attendances', '/hr/rectify/attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_hr_rectify_attendances(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'employee_id desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
                                                
        searchbar_filters = {
            'all': {'label': _('Valid'), 'domain': []},
            'invalid': {'label': _('In-Valid'), 'domain': []},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in No#')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')},
        }
        
        searchbar_groupby = {
            'id': {'input': 'id', 'label': _('None')},
        }
        date = fields.date.today() - timedelta(30)
        project_groups = request.env['hr.attendance.rectification'].sudo().search([('employee_id.user_id','=', http.request.env.context.get('uid'))])
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'ID'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('employee_id.name', 'Employee'):
                search_domain = OR([search_domain, [('employee_id.name', 'ilike', search)]])
            domain += search_domain
        domain += [('employee_id.user_id', '=', http.request.env.context.get('uid'))] 
        rectify_count = request.env['hr.attendance.rectification'].search_count(domain)
        pager = portal_pager(
            url="/hr/rectify/attendances",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=rectify_count,
            page=page,
            step=self._items_per_page
        )
        _rectification = request.env['hr.attendance.rectification'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_rectify_attendance_history'] = _rectification.ids[:100]
        grouped_rectify_attendances = [project_groups]
        paging(0,0,1)
        paging(grouped_rectify_attendances)
        
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_rectify_attendances': grouped_rectify_attendances,
            'page_name': 'rectify',
            'default_url': '/hr/rectify/attendances',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_attendance.portal_hr_rectify_attendances", values)
    
    
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'attendance_count' in counters:
            values['attendance_count'] = request.env['hr.attendance'].search_count([])
        return values
  
    def _attendance_get_page_view_values(self,attendance, next_id = 0,pre_id= 0, attendance_user_flag = 0, access_token = None, **kwargs):
        values = {
            'page_name' : 'Attendance',
            'attendance' : attendance,
            'attendance_user_flag': attendance_user_flag,
            'next_id' : next_id,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(attendance, access_token, values, 'my_attendance_history', False, **kwargs)

    @http.route(['/hr/attendances', '/hr/attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_hr_attendances(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'employee_id desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
                                                
        searchbar_filters = {
            'all': {'label': _('Valid'), 'domain': [('in_validity','=','valid')]},
            'invalid': {'label': _('In-Valid'), 'domain': [('in_validity','=','invalid')]},
        }
           
        searchbar_inputs = {
            'in_validity': {'input': 'in_validity', 'label': _('Search in Validity')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }
        date = fields.date.today() - timedelta(70)
        project_groups = request.env['hr.attendance'].search([('att_date','>=', date)])
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        if filterby == 'invalid':
            filterby = 'invalid'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
#         domain = []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]       

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'ID'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('employee_id.name', 'Employee'):
                search_domain = OR([search_domain, [('employee_id.name', 'ilike', search)]])
            domain += search_domain
        domain += [('employee_id.user_id', '=', http.request.env.context.get('uid'))]
        
        attendance_count = request.env['hr.attendance'].sudo().search_count(domain)

        pager = portal_pager(
            url="/hr/attendances",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=attendance_count,
            page=page,
            step=self._items_per_page
        )

        _attendances = request.env['hr.attendance'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_attendance_history'] = _attendances.ids[:100]

        grouped_attendances = [project_groups]
        ora_att_date = fields.date.today() - timedelta(30)

        if filterby == 'all':
            att_attendances = request.env['hr.attendance'].sudo().search([ ('employee_id.user_id', '=', http.request.env.context.get('uid') ), ('att_date','>=', ora_att_date ),('in_validity','=','valid'), ('out_validity', '=', 'valid') ])
        if  filterby == 'invalid': 
            att_attendances = request.env['hr.attendance'].sudo().search([ ('employee_id.user_id', '=', http.request.env.context.get('uid') ), ('att_date','>=', ora_att_date ), '|',('in_validity','=','invalid'), ('out_validity', '=', 'invalid') ])
        paging(0,0,1)
        paging(grouped_attendances)
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_attendances': grouped_attendances,
            'att_attendances': att_attendances,
            'page_name': 'attendance',
            'default_url': '/hr/attendances',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_attendance.portal_hr_attendances", values)   

   
