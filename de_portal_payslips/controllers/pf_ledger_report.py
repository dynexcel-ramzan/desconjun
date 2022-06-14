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

def pf_page_content(flag = 0):
    employee = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))], limit=1)
    
    return {
        'employee_name': employee,
        'success_flag' : flag,
        'date_from':  fields.date.today().replace(month=7,day=1, year=fields.date.today().year-1),
        'date_to': fields.date.today().replace(day=27),
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
        

class PFLedgerReport(http.Controller):

    @http.route('/pf/ledger/report/',type="http", website=True, auth='user')
    def action_print_pf_ledger_reports(self, **kw):
        return request.render("de_portal_payslips.print_pf_ledger_report", pf_page_content())
    
    

class CustomerPortal(CustomerPortal):
    
 
    
    def _show_report_portal_pf(self, model, report_type, employee, start_date, end_date,  report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s", report_type))

        report_sudo = request.env.ref(report_ref).with_user(SUPERUSER_ID)

        if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
            raise UserError(_("%s is not the reference of a report", report_ref))

        if hasattr(model, 'company_id'):
            report_sudo = report_sudo.with_company(model.company_id)

        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(report_sudo, method_name)([model], data={'report_type': report_type,'employee': employee,'start_date':start_date,'end_date':end_date})[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)


    
    @http.route('/hr/pf/ledger/report/',type="http", website=True,download=False, auth='user')
    def action_print_employee_pf_report(self, **kw):
        report_type='pdf'
        order_sudo = 'partner.pf.ledger'
        download = False
        employee = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))], limit=1).id
        start_date = kw.get('check_in')
        end_date = kw.get('check_out')
        return self._show_report_portal_pf(model=order_sudo, report_type=report_type, employee=employee, start_date=start_date, end_date=end_date, report_ref='de_account_pf_ledger.open_pf_ledger_report', download=download)
    
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'pf_count' in counters:
            values['pf_count'] = request.env['hr.payslip'].search_count([])
        return values
  
    def _pf_get_page_view_values(self,pf, next_id = 0,pre_id= 0, pf_user_flag = 0, access_token = None, **kwargs):
        values = {
            'page_name' : 'pf',
            'pf' : pf,
            'pf_user_flag': pf_user_flag,
            'next_id' : next_id,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(pf, access_token, values, 'my_pf_history', False, **kwargs)

    @http.route(['/pf/ledgers', '/pf/ledgers/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_ledgers(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
                                                
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
          
        }   
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in No#')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')},         

        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
#         domain = []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]   
            
        domain += [('employee_id.user_id','=',http.request.env.context.get('uid'))]       
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('number', 'all'):
                search_domain = OR([search_domain, [('number', 'ilike', search)]])
            if search_in in ('employee_id.name', 'all'):
                search_domain = OR([search_domain, [('employee_id.name', 'ilike', search)]])
            domain += search_domain
        pf_count = request.env['hr.payslip'].search_count(domain)
        pager = portal_pager(
            url="/pf/ledgers",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=pf_count,
            page=page,
            step=self._items_per_page
        )
        _pf_ledgers = request.env['partner.pf.ledger'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_pf_history'] = _pf_ledgers.ids[:100]
        grouped_pf_ledgers = [_pf_ledgers]        
        paging(0,0,1)
        paging(grouped_pf_ledgers)
        
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_pf_ledgers': grouped_pf_ledgers,
            'page_name': 'pf',
            'default_url': '/pf/ledgers',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_payslips.portal_my_pf_ledgers", values)   

   
