from odoo import api, fields, models, _
from calendar import monthrange

from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    site_incharge_id = fields.Many2one('hr.employee', string="Incharge")
    site_user_id = fields.Many2one(related='site_incharge_id.user_id', string="Incharge User")
    effective_date = fields.Date(string='Effective Date')

    def action_update_bank_account(self):
        for rec in self:
            is_account = False
            bank_account = ''
            address = ''
            bank_id  = 0
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['hr.employee'].browse(selected_ids)
            if rec.bank_account_id:
                is_account = True
                bank_account = rec.bank_account_id.acc_number
                bank_id = rec.bank_account_id.bank_id.id
            if  rec.address_home_id:
                address = rec.address_home_id.street
        return {
            'name': ('Add Bank Account'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.bank.account.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_employee_ids': selected_records.ids, 'default_is_account': is_account, 'default_note': 'Employee Already Bank Account Exist! Do you want to change than proceed.', 'default_bank_id': bank_id, 'default_bank_account': bank_account, 'default_address': address },
        }
    
    def action_assign_incharge(self):
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['hr.employee'].browse(selected_ids)
        return {
            'name': ('Attendance Incharge'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'site.incharge.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_employee_ids': selected_records.ids},
        }


    def action_update_resignation(self):
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['hr.employee'].browse(selected_ids)
        return {
            'name': ('Resignation'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.resign.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_employee_ids': selected_records.ids},
        }
    
    def action_assign_manager(self):
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['hr.employee'].browse(selected_ids)
        return {
            'name': ('Manager'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.manager.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_employee_ids': selected_records.ids},
        }
        
    

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
  