# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class TimesheetReportWizard(models.TransientModel):
    _name = "timesheet.report.wizard"
    _description = "Timesheet Report wizard"

    employee_ids = fields.Many2many('hr.employee', string='Employee')
    start_date = fields.Date(string='From Date', required='1', help='select start date')
    end_date = fields.Date(string='To Date', required='1', help='select end date')
    type = fields.Selection([
        ('summary', 'Summary'),
        ('detail', 'Detail')],
        readonly=False, string='Type', index=True , default='summary')

    def check_report(self):
        data = {}
        data['form'] = self.read(['type','start_date', 'end_date','employee_ids'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['type','start_date', 'end_date','employee_ids'])[0])
        return self.env.ref('de_timesheet_portal.open_site_sheet_report_wizard_action').report_action(self, data=data, config=False)