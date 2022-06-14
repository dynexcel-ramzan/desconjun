# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class PFLedgerWizard(models.TransientModel):
    _name = "pf.ledger.wizard"
    _description = "PF Ledger wizard"
    

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    

    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from','date_to','employee_id'])[0]
        return self._print_report(data)

    
    def _print_report(self, data):
        data['form'].update(self.read(['date_from','date_to','employee_id'])[0])
        return self.env.ref('de_account_pf_ledger.open_pf_ledger_report').report_action(self, data=data, config=False)
    