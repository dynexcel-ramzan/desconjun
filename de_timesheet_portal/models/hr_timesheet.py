# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero, float_repr
from odoo.tools.misc import clean_context, format_date
from dateutil.relativedelta import relativedelta

class HRTimesheetSheetType(models.Model):
    _name = 'hr.timesheet.sheet.type'
    _description = 'Timesheet Report Type'
    _order = 'sequence, stage_category, id'
        
    name = fields.Char(string='Stage Name', required=True, translate=True)
    stage_code = fields.Char(string='Code', size=3, copy=False, required=True)
    description = fields.Text(
        "Requirements", help="Enter here the internal requirements for this stage. It will appear "
                             "as a tooltip over the stage's name.", translate=True)
    sequence = fields.Integer(default=1, required=True)
    
    department_id = fields.Many2one('hr.department', copy=True, string="Department")
    
    stage_category = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], string='Category', default='draft')
    
    validation_type = fields.Selection([
        ('no_validation', 'No Validation'),
        ('group', 'By Security Group'),
        ('manager', "By Employee's Manager"),
        ], default='no_validation', string='Validation Type', required=True)
    
    group_id = fields.Many2one('res.groups', string='Security Group')
    manager_approval_level = fields.Integer(string='Manager Approval Level')
    
    _sql_constraints = [
        ('code_uniq', 'unique (stage_code)', "Code already exists!"), 
    ]
            
    
    
class HRTimesheetSheet(models.Model):
    _name = 'hr.timesheet.sheet'
    _description = 'Timehseet Sheet'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin', 'rating.mixin']
    _mail_post_access = 'read'
    
    def _domain_employee_id(self):
        if not self.user_has_groups('hr_timesheet.group_hr_timesheet_approver'):
            return [('user_id', '=', self.env.user.id)]
        return []
    
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        return self.stage_find([])
    
    READONLY_STATES = {
        'reported': [('readonly', True)],
        'pending': [('readonly', True)],
        'approved': [('readonly', True)],
        'done': [('readonly', True)],
        'refused': [('readonly', True)],
    }

    
    name = fields.Char(required=True, translate=True)
    date = fields.Date(string='Date', required=True)
    
    employee_id = fields.Many2one('hr.employee', "Employee", domain=_domain_employee_id, required=True, context={'active_test': False}, states=READONLY_STATES,)
    department_id = fields.Many2one('hr.department', compute='_compute_from_employee_id', readonly=True, copy=True, string="Department")

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)


    validated_status = fields.Selection([('draft', 'Draft'), 
                                         ('validated', 'Validated'),
                                        ('cancel', 'Cancel')], default='draft', required=True, store=True)

    timesheet_line_ids = fields.One2many('account.analytic.line', 'sheet_id', string='Expense Lines', copy=False, states=READONLY_STATES)
    
    total_hours = fields.Float(string='Total Hours', compute='_compute_all_hours', store=True, states=READONLY_STATES)
    planned_hours = fields.Float(string='Planneed Hours', compute='_compute_all_hours')
    diff_hours = fields.Float(string='Diff. Hours', compute='_compute_all_hours', store=True, states=READONLY_STATES)
    
    timesheets_report_count = fields.Integer(compute='_compute_timesheets_report_count')
    
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('refused', 'Refused'),
    ], string='Status', compute='_compute_state', copy=False, index=True, readonly=True, store=True, default='draft', help="Status of request.")
    
    request_id = fields.Many2one('approval.request', readonly=True, copy=False, string="Approval Request")
    user_status = fields.Selection(related='request_id.user_status')

    @api.depends('request_id','request_id.request_status')
    def _compute_state(self):
        for sheet in self:
            if sheet.request_id.request_status == 'approved':
                sheet.state = 'approved'
               
            else:
                sheet.state = sheet.state                
                
    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for sheet in self:
            sheet.department_id = sheet.employee_id.department_id

            
    def _compute_stage_id(self):
        for sheet in self:
            sheet.stage_id = sheet.stage_find([])
      
    
    def stage_find(self, domain=[], order='sequence'):        
        search_domain = []
        search_domain += list(domain)
        return self.env['hr.timesheet.sheet.type'].search(search_domain, order=order, limit=1).id
    
    
    @api.depends('timesheet_line_ids','timesheet_line_ids.unit_amount')
    def _compute_all_hours(self):
        for ts in self:
            pln_hrs = 0
            tot_hrs = 0
            date_passed = 0
            general_shift = self.env['resource.calendar'].sudo().search([('shift_type','=','general')], limit=1)
            for line in ts.timesheet_line_ids.sorted(key=lambda r: r.line_date):
                rest_day = '0'
                if str(date_passed)!=str(line.line_date):
                    date_passed=line.line_date
                    shift_schedule_line = self.env['hr.shift.schedule.line'].sudo().search([('employee_id','=',ts.employee_id.id),('date','=',line.line_date),('state','=','posted')], limit=1)
                    if not shift_schedule_line:
                        pln_hrs += general_shift.hours_per_day  
                        
                    pln_hrs += shift_schedule_line.first_shift_id.hours_per_day
                    if shift_schedule_line.rest_day==True:
                        rest_day = '1'    
                    if shift_schedule_line:
                        if shift_schedule_line.first_shift_id:
                            general_shift = shift_schedule_line.first_shift_id
                        else:
                            general_shift = shift_schedule_line.second_shift_id
                    if shift_schedule_line.second_shift_id:
                        pln_hrs += shift_schedule_line.second_shift_id.hours_per_day                               
                tot_hrs += line.unit_amount
                
                for gazetted_day in general_shift.global_leave_ids:
                    gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                    gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                    if str(line.line_date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(line.line_date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')): 
                        rest_day = '1'
                if rest_day=='1':        
                    line.update({
                        'rest_day':  True
                    })
            if pln_hrs < 0:
                pln_hrs = 0
            if tot_hrs < 0:
                tot_hrs = 0  
            diff_hrs = pln_hrs - tot_hrs 
            if diff_hrs < 0:
                diff_hrs=0
            ts.total_hours = tot_hrs
            ts.planned_hours = pln_hrs
            ts.diff_hours = diff_hrs
            
            
    def _compute_timesheets_report_count(self):
        for report in self:
            report.timesheets_report_count = len(report.timesheet_line_ids)
            
    def action_submit_sheet(self):
        self._action_approval()
        self.write({'state': 'pending'})
    
    def _action_approval(self):
        
        vals = {}
        for sheet in self:
            approval_category_id = self.env['approval.category'].search([('name','=','Timesheet'),('company_id','=',sheet.employee_id.company_id.id)],limit=1)
            vals = {
                    'name': 'Timesheet',
                    'is_parent_approver': True,
                    'company_id': sheet.employee_id.company_id.id,
                    }
            approval_category_id = self.env['approval.category'].sudo().create(vals)
            if approval_category_id:
                vals = {
                    'name': sheet.name,
                    'request_owner_id': sheet.employee_id.user_id.id,
                    'request_status': 'new',
                    'category_id': approval_category_id.id
                }
                request_id = self.env['approval.request'].sudo().create(vals)
                request_id.action_confirm()
                sheet.request_id = request_id.id
    
    def action_approve(self):
        for sheet in self:
            sheet.request_id.sudo().action_approve()
            
    def action_refuse(self):
        for sheet in self:
            sheet.update({
                'state': 'refused' 
            })
            
    def action_draft(self):
        for sheet in self:
            sheet.request_id.sudo().action_refuse()
            sheet.update({
                'state': 'draft'
            })       
            
    def action_reject1(self):
        stage_id = self.env['hr.timesheet.sheet.type']
        for sheet in self:
            stage_id = self.env['hr.timesheet.sheet.type'].search([('stage_category','=','cancel')],limit=1)
            sheet.stage_id = stage_id.id
            
    
            
class HRTimesheetType(models.Model):
    _name = 'hr.timesheet.type'
    _description = 'Timesheet Type'

    name = fields.Char(required=True, translate=True)

    
class HRTimesheet(models.Model):
    _inherit = 'account.analytic.line'
    
    sheet_id = fields.Many2one('hr.timesheet.sheet', string="Timesheet Report", domain="[('employee_id', '=', employee_id), ('company_id', '=', company_id)]", readonly=True, copy=False)
    timesheet_type_id = fields.Many2one('hr.timesheet.type', "Type", required=True)
    
    unit_amount_from = fields.Float('Time From', default=0.0)
    unit_amount_to = fields.Float('Time To', default=0.0)
    line_date = fields.Date(string='Line Date')
    ora_date = fields.Date(string='ORA Date')
    rest_day = fields.Boolean(string='Rest Day')

    
    @api.constrains('timesheet_type_id')
    def _check_timesheet(self):
        for line in self:
            if line.timesheet_type_id:
                task = self.env['project.task'].sudo().search([('name','=',line.timesheet_type_id.name)], limit=1)
                line.task_id = task.id
            
    
    @api.constrains('line_date')
    def _check_line_date(self):
        for line in self:
            in_existing_timesheet = self.env['account.analytic.line'].search([('id','!=',line.id),('employee_id','=',line.sheet_id.employee_id.id),('line_date','=',line.line_date),('unit_amount_from','<=',line.unit_amount_from),('unit_amount_to','>=',line.unit_amount_from),('sheet_id.state','!=','refused')], limit=1)
            
            out_existing_timesheet = self.env['account.analytic.line'].search([('id','!=',line.id),('employee_id','=',line.sheet_id.employee_id.id),('line_date','=',line.line_date),('unit_amount_from','<=',line.unit_amount_to),('unit_amount_to','>=',line.unit_amount_to),('sheet_id.state','!=','refused')], limit=1)
            if in_existing_timesheet:
                raise UserError('Timesheet Entry Already Exist for this Date! '+str(in_existing_timesheet.line_date) +' Time From: '+str(in_existing_timesheet.unit_amount_from)+' Time To: '+str(in_existing_timesheet.unit_amount_to))
            if out_existing_timesheet:
                raise UserError('Timesheet Entry Already Exist for this Date! '+str(out_existing_timesheet.line_date) +' Time From: '+str(out_existing_timesheet.unit_amount_from)+' Time To: '+str(out_existing_timesheet.unit_amount_to))    
    
    
    
    def action_delete(self):
        for timesheet in self:
            timesheet.unlink()
    


