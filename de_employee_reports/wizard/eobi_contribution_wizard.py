# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class EOBIContributionWizard(models.TransientModel):
    _name = "eobi.contribution.wizard"
    _description = "EOBI Contribution wizard"

    location_ids = fields.Many2many('hr.work.location', string='Work Locations')
    date = fields.Date(string='Date', required=True, default=fields.date.today().replace(day=15))
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company )
    
    
    

    def check_report(self):
        data = {}
        data['form'] = self.read(['company_id', 'date', 'location_ids'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['company_id', 'date', 'location_ids'])[0])
        return self.env.ref('de_employee_reports.eobi_contribution_report').report_action(self, data=data, config=False)