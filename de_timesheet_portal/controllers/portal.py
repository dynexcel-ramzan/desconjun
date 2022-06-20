# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from operator import itemgetter

from markupsafe import Markup
from datetime import datetime , date
from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError
from odoo.http import request
from odoo.tools.translate import _
from odoo.tools import groupby as groupbyelem
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
from odoo.osv.expression import OR, AND
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


def print_site_timesheet_content(flag=0):
    emps = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    employee_name = emps
    return {
        'emps': emps,
        'employee_name': employee_name,
        'success_flag' : flag,
    }

class CreateAttendance(http.Controller):
    
    @http.route('/site/timesheet/print/',type="http", website=True, auth='user')
    def action_print_site_timesheet(self, **kw):
        return request.render("de_timesheet_portal.print_site_timesheet_report", print_site_timesheet_content())
    
   


class CustomerPortal(CustomerPortal):
    
    def _show_report_site_sheet(self, model, report_type, ora_type, employee, start_date, end_date, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s", report_type))
        report_sudo = request.env.ref(report_ref).with_user(SUPERUSER_ID)
        if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
            raise UserError(_("%s is not the reference of a report", report_ref))
        if hasattr(model, 'company_id'):
            report_sudo = report_sudo.with_company(model.company_id)
        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(report_sudo, method_name)([model], data={'report_type': report_type,'employee':employee,'ora_type': ora_type, 'start_date':start_date,'end_date':end_date})[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)


    
    @http.route('/site/timesheet/print/report',type="http", website=True,download=False, auth='user')
    def action_print_site_sheet_report(self, **kw):
        report_type='pdf'
        order_sudo = 'account.analytic.line'
        download = False
        employee = request.env['hr.employee'].sudo().search([('id','=',int(kw.get('employee_id')))])
        start_date = kw.get('check_in')
        ora_type = kw.get('type')
        end_date = kw.get('check_out')
        return self._show_report_site_sheet(model=order_sudo, report_type=report_type, ora_type=ora_type ,employee=employee, start_date=start_date, end_date=end_date, report_ref='de_timesheet_portal.open_site_sheet_report_wizard_action', download=download)
    
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'timesheet_report_count' in counters:
            values['timesheet_report_count'] = request.env['hr.timesheet.sheet'].sudo().search_count([]) \
                if request.env['hr.timesheet.sheet'].check_access_rights('read', raise_exception=False) else 0
        if 'timesheet_count' in counters:
            values['timesheet_count'] = request.env['account.analytic.line'].sudo().search_count([]) \
                if request.env['account.analytic.line'].check_access_rights('read', raise_exception=False) else 0
        return values
    
    # timesheet report page
    @http.route(['/my/timelogs', '/my/timelogs/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_timelogs(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Sheet = request.env['hr.timesheet.sheet']
        domain = []

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']
        # Timesheet Report count
        
        domain += ['|',('employee_id.parent_id.user_id','=',http.request.env.context.get('uid')),('employee_id.user_id','=',http.request.env.context.get('uid'))]
        timesheet_report_count = Sheet.sudo().search_count(domain)
        # pager
        
        pager = portal_pager(
            url="/my/timelogs",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=timesheet_report_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        sheets = Sheet.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_report_timesheets_history'] = sheets.ids[:100]
        
        project_list = []
        project_obj = request.env['project.project'].sudo().search([])
        for project in project_obj:
            project_list.append({
                'name': project.name, 
                'id': project.id
            })
        values['project_list'] = project_list
        values.update({
            'sheets': sheets,
            'page_name': 'timelogs_report',
            'default_url': '/my/timelogs',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("de_timesheet_portal.portal_my_timelogs", values)
    
    # ------------------------------------------------------------
    # My Timesheet
    # ------------------------------------------------------------
    def _timesheet_get_page_view_values(self, timesheet, access_token, **kwargs):
        sheet = kwargs.get('sheet')
        if sheet:
            sheet_accessible = True
            page_name = 'report_timelog'
            history = 'my_report_timelogs_history'
        else:
            page_name = 'sheet'
            history = 'my_timelogs_history'
            try:
                sheet_accessible = bool(timesheet.sheet_id.id and self._document_check_access('hr.timesheet.sheet', timesheet.sheet_id.id))
            except (AccessError, MissingError):
                sheet_accessible = False
        values = {
            'page_name': page_name,
            'timesheet': timesheet,
            'user': request.env.user,
            'sheet_accessible': sheet_accessible,
        }
        return self._get_page_view_values(timesheet, access_token, values, history, False, **kwargs)
    
    def _sheet_get_page_view_values(self, sheet, access_token, **kwargs):
        values = {
            'sheet': sheet,
            'timesheets': sheet.timesheet_line_ids,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'report_type': 'html',
        }
        history = request.session.get('my_timelogs_history', [])
        values.update(get_records_pager(history, sheet))

        return values
    
    # ------------------------------------------------
    # ---------Project & task render values ----------
    # ------------------------------------------------
    def _get_project_task_render_values(self, kw, render_values):
        '''
        This method provides fields related to the project to render the website sale form
        '''
        projects = request.env['project.project'].sudo().search([])
        type_ids = request.env['hr.timesheet.type'].sudo().search([])
        res = {
            'task_ids': projects.get_website_sale_tasks(),
            'projects': projects.get_website_sale_projects(),
            'type_ids': type_ids,
        }
        return res
    
    
    @http.route(['/my/timelog/<int:sheet_id>'], type='http', auth="public", website=True)
    def portal_timesheet_page(self, sheet_id=None, access_token=None, message=False, download=False, **kw):

        try:
            sheet_sudo = request.env['hr.timesheet.sheet'].sudo().search([('id', '=', int(sheet_id))])
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        type_list = [];
        project_list = [];
       
        if sheet_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_request_%s' % sheet_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_request_%s' % sheet_sudo.id] = now
                body = _('Quotation viewed by customer %s', sheet_sudo.employee_id.name)
                _message_post_helper(
                    "hr.timesheet.sheet",
                    sheet_sudo.id,
                    body,
                    token=sheet_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )
        
        values = self._sheet_get_page_view_values(sheet_sudo, access_token, **kw)
        render_values = {
            'callback': kw.get('callback'),
        }
        values.update(self._get_project_task_render_values(kw, render_values))
        
        type_obj = request.env['hr.timesheet.type'].sudo().search([])
        for type in type_obj:
            type_list.append({
                'name': type.name, 
                'id': type.id
            })
        values['type_list'] = type_list
        
        project_obj = request.env['project.project'].sudo().search([])
        for project in project_obj:
            project_list.append({
                'name': project.name, 
                'id': project.id
            })
        values['project_list'] = project_list
        
        values['message'] = message
        message = kw.get('decline_message')
        return request.render('de_timesheet_portal.portal_my_timelog', values)
    
    # --------------------------------------------
    # ------------- Submit Request ---------------
    # --------------------------------------------
    @http.route([
        '/my/timelog/submit/<int:sheet_id>',
    ], type='http', auth="public", website=True)
    def sheet_submit(self, sheet_id=None, access_token=None, **kw):
        try:
            sheet_sudo = self._document_check_access('hr.timesheet.sheet', sheet_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if sheet_sudo:
            sheet_sudo.sudo().action_submit_sheet()
        return request.redirect('/my/timelog/%s' % (sheet_sudo.id))
    
    
    # --------------------------------------------
    # ------------- Accept Request ---------------
    # --------------------------------------------
    @http.route([
        '/my/timelog/approve/<int:sheet_id>',
        '/my/timelog/delete/<int:sheet_id>/<access_token>',
    ], type='http', auth="public", website=True)
    def sheet_approve(self, sheet_id=None, access_token=None, **kw):
        try:
            sheet_sudo = self._document_check_access('hr.timesheet.sheet', sheet_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        sheet_sudo = request.env['hr.timesheet.sheet'].sudo().browse(int(sheet_id))
        if sheet_sudo:
            sheet_sudo.sudo().action_approve()
        return request.redirect('/my/timelog/%s' % (sheet_sudo.id))
    
    # ------------------------
    # Reject request
    # ------------------------
    @http.route([
        '/my/timelog/draft/<int:sheet_id>',
        '/my/timelog/draft/<int:sheet_id>/<access_token>',
    ], type='http', auth="public", website=True)
    def request_draft(self, sheet_id=None, access_token=None, **kw):
        try:
            sheet_sudo = self._document_check_access('hr.timesheet.sheet', sheet_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        body = _('request rejected')
        sheet_sudo.with_context(mail_create_nosubscribe=True).message_post(body=body, message_type='comment', subtype_xmlid='mail.mt_note')
        
        message = kw.get('decline_message')

        query_string = False
        sheet_sudo.action_draft()
        if message:
            sheet_sudo.action_draft()
            _message_post_helper('hr.timesheet.sheet', sheet_id, message, **{'token': access_token} if access_token else {})
        else:
            query_string = "&message=cant_reject"

        return request.redirect('/my/timelog/%s' % (sheet_id))
    
    
    # ------------------------
    # Reject request
    # ------------------------
    @http.route([
        '/my/timelog/reject/<int:sheet_id>',
        '/my/timelog/reject/<int:sheet_id>/<access_token>',
    ], type='http', auth="public", website=True)
    def request_reject(self, sheet_id=None, access_token=None, **kw):
        try:
            sheet_sudo = self._document_check_access('hr.timesheet.sheet', sheet_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        body = _('request rejected')
        sheet_sudo.with_context(mail_create_nosubscribe=True).message_post(body=body, message_type='comment', subtype_xmlid='mail.mt_note')
        
        message = kw.get('decline_message')

        query_string = False
        sheet_sudo.action_refuse()
        if message:
            sheet_sudo.action_refuse()
            _message_post_helper('hr.timesheet.sheet', sheet_id, message, **{'token': access_token} if access_token else {})
        else:
            query_string = "&message=cant_reject"

        return request.redirect('/my/timelog/%s' % (sheet_id))
    
    # ------------------------
    # Update  request
    # ------------------------
    @http.route([
        '/my/timelog/edit/<int:sheet_id>',
        '/my/timelog/edit/<int:sheet_id>/<access_token>',
    ], type='http', auth="public", website=True)
    def update_request(self, sheet_id=None, access_token=None, **kw):
        try:
            sheet_sudo = self._document_check_access('hr.timesheet.sheet', sheet_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        timesheet = request.env['account.analytic.line']
        values = {}
        timesheet_id = kw.get('timesheet_id')
        if timesheet_id:
            timesheet = request.env['account.analytic.line'].sudo().search([('id','=',int(timesheet_id))],limit=1)
        values = {
            'name': kw.get('name')
        }
        timesheet.write(values)

        return request.redirect('/my/timelog/%s' % (sheet_id))
    

    
    @http.route([
        '/my/timelog/delete/<int:timesheet_id>',
    ], type='http', auth="public", website=True)
    def timesheet_delete(self, timesheet_id=None, access_token=None, **kw):
        timesheet = request.env['account.analytic.line'].sudo().browse(int(timesheet_id))
        if timesheet:
            sheet_sudo = request.env['hr.timesheet.sheet'].sudo().search([('id', '=', int(timesheet.sheet_id.id))],limit=1)
            timesheet.sudo().unlink()
        return request.redirect('/my/timelog/%s' % (sheet_sudo.id))
    
    
    @http.route([
        '/my/timelog/add',
    ], type='http', auth="public", website=True)
    def timesheet_add(self, **kw):
        employee_id = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
        vals = {
            'employee_id': employee_id.id,
            'name': kw.get('name'),
            'date': fields.date.today(),
        }
        sheet_id = request.env['hr.timesheet.sheet'].sudo().create(vals)
        sheet_id.update({
            'date': fields.date.today(),
        })
        return request.redirect('/my/timelog/%s' % (sheet_id.id))
    
    @http.route([
        '/my/timelog/add/line',
    ], type='http', auth="public", website=True)
    def timesheet_add_line(self, access_token=None,**kw):
        sheet = request.env['hr.timesheet.sheet'].sudo().browse(int(kw.get('sheet_id')),)
        vals = {}
        values ={}
        time_from = datetime.strptime(kw.get('unit_amount_from'), '%H:%M')
        time_to = datetime.strptime(kw.get('unit_amount_to'), '%H:%M')
        unit_time_from = str(time_from.hour)+'.'+ str(time_from.minute)
        unit_time_to = str(time_to.hour)+'.'+ str(time_to.minute)
        if float(unit_time_from) > float(unit_time_to):
            warning_message='Out Time cannot be Less than In Time! '+ "\n"+' Time From: '+str(unit_time_from)+ "\n"+' Time To: '+str(unit_time_to)
            values = self._sheet_get_page_view_values(sheet, access_token, **kw)
            values.update({
                'sheet': sheet,
                'error_flag': 1,
                'errora_message': warning_message,
                'projects': request.env['project.project'].sudo().search([]),
                'type_ids': request.env['hr.timesheet.type'].sudo().search([]),
                'name': kw.get('name'),
                'project_id_ora': int(kw.get('project_id')),
                'task_id_ora': int(kw.get('task_id')),
                'unit_amount_from': kw.get('unit_amount_from'),
                'unit_amount_to': kw.get('unit_amount_to'),
                'date': kw.get('date'),
            })
            return request.render('de_timesheet_portal.portal_my_timelog', values)  
        if kw.get('date') > str(fields.date.today()):
            warning_message='Not Allow to Add Timesheet for Future Date!'
            values = self._sheet_get_page_view_values(sheet, access_token, **kw)
            values.update({
                'sheet': sheet,
                'error_flag': 1,
                'errora_message': warning_message,
                'projects': request.env['project.project'].sudo().search([]),
                'type_ids': request.env['hr.timesheet.type'].sudo().search([]),
                'name': kw.get('name'),
                'project_id_ora': int(kw.get('project_id')),
                'task_id_ora': int(kw.get('task_id')),
                'unit_amount_from': kw.get('unit_amount_from'),
                'unit_amount_to': kw.get('unit_amount_to'),
                'date': kw.get('date'),
            })
            return request.render('de_timesheet_portal.portal_my_timelog', values)  
        in_existing_timesheet = request.env['account.analytic.line'].sudo().search([('employee_id','=',sheet.employee_id.id),('line_date','=',kw.get('date')),('unit_amount_from','<=',unit_time_from),('unit_amount_to','>=',unit_time_from),('sheet_id.state','!=','refused')], limit=1)
        out_existing_timesheet = request.env['account.analytic.line'].sudo().search([('employee_id','=',sheet.employee_id.id),('line_date','=',kw.get('date')),('unit_amount_from','<=',unit_time_to),('unit_amount_to','>=',unit_time_to),('sheet_id.state','!=','refused')], limit=1)
        if in_existing_timesheet:
            warning_message='Timesheet Entry Already Exist! '+ "\n"+'Date: ' +str(in_existing_timesheet.line_date.strftime('%d-%b-%y'))+ "\n"+' Time From: '+str(in_existing_timesheet.unit_amount_from)+ "\n"+' Time To: '+str(in_existing_timesheet.unit_amount_to)
            values = self._sheet_get_page_view_values(sheet, access_token, **kw)
            values.update({
                'sheet': sheet,
                'error_flag': 1,
                'errora_message': warning_message,
                'projects': request.env['project.project'].sudo().search([]),
                'type_ids': request.env['hr.timesheet.type'].sudo().search([]),
                'name': kw.get('name'),
                'project_id_ora': int(kw.get('project_id')),
                'task_id_ora': int(kw.get('task_id')),
                'unit_amount_from': kw.get('unit_amount_from'),
                'unit_amount_to': kw.get('unit_amount_to'),
                'date': kw.get('date'),
            })
            return request.render('de_timesheet_portal.portal_my_timelog', values)

        if out_existing_timesheet:
            warning_message='Timesheet Entry Already Exist! '+"\n"+'Date: '+str(out_existing_timesheet.line_date.strftime('%d-%b-%y') )+ "\n" +' Time From: '+str(out_existing_timesheet.unit_amount_from)+ "\n"+' Time To:   '+str(out_existing_timesheet.unit_amount_to)
            values = self._sheet_get_page_view_values(sheet, access_token, **kw)
            values.update({
                'sheet': sheet,
                'error_flag': 1,
                'errora_message': warning_message,
                'projects': request.env['project.project'].sudo().search([]),
                'type_ids': request.env['hr.timesheet.type'].sudo().search([]),
                'name': kw.get('name'),
                'project_id_ora': int(kw.get('project_id')),
                'task_id_ora': int(kw.get('task_id')),
                'unit_amount_from': kw.get('unit_amount_from'),
                'unit_amount_to': kw.get('unit_amount_to'),
                'date': kw.get('date'),
            })
            return request.render('de_timesheet_portal.portal_my_timelog', values)
        vals = {
            'sheet_id': sheet.id,
            'project_id': int(kw.get('project_id')),
            'timesheet_type_id': int(kw.get('task_id')),
            'name': kw.get('name'),
            'unit_amount_from': float(unit_time_from),
            'unit_amount_to': float(unit_time_to),
            'unit_amount': float(unit_time_to) - float(unit_time_from),
            'date': kw.get('date'),
            'line_date': kw.get('date'),
            'employee_id': sheet.employee_id.id
        }
        timesheet_id = request.env['account.analytic.line'].sudo().create(vals)
        return request.redirect('/my/timelog/%s' % (sheet.id))


