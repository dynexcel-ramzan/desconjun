
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AddBankAccWizard(models.TransientModel):
    _name = "add.bank.account.wizard"
    _description = "Add Bank Account Wizard"
    

    bank_account = fields.Char(string='Account Number', required=True)
    bank_id = fields.Many2one('res.bank', string='Bank', required=True)
    address = fields.Char(string='Employee Address')
    note = fields.Char(string='Note')
    is_account = fields.Boolean(string='Is Account')
    employee_ids = fields.Many2many('hr.employee', string='Employee')    
    
    def action_update_bank(self):
        for employee in self.employee_ids:
            if employee.address_home_id:
                bank_acc = self.env['res.partner.bank'].search([('acc_number','=', self.bank_account)], limit=1)
                if not bank_acc:
                    bank_line_vals = {
                        'acc_number' :  self.bank_account ,
                        'acc_type':  'bank' ,
                        'bank_id':  self.bank_id.id, 
                        'acc_holder_name': employee.address_home_id.name ,
                        'company_id':  employee.company_id.id ,
                        'partner_id': employee.address_home_id.id ,
                    }
                    bank_acc = self.env['res.partner.bank'].create(bank_line_vals)
                    
                employee.update({
                    'address_home_id':  employee.address_home_id.id,
                    'bank_account_id':  bank_acc,
                })    
            if not employee.address_home_id:
                vals = {
                    'company_type': 'person',
                    'name': employee.name,
                    'street': self.address,
                    'email':  employee.work_email,
                    'company_id': employee.company_id.id, 
                }
                partner = self.env['res.partner'].create(vals)
                
                bank_acc = self.env['res.partner.bank'].search([('acc_number','=', self.bank_account)], limit=1)
                if not bank_acc:
                    bank_line_vals = {
                        'acc_number' :  self.bank_account,
                        'acc_type':  'bank' ,
                        'acc_holder_name': partner.name,
                        'company_id':  employee.company_id.id,
                        'partner_id': partner.id ,
                    }
                    bank_acc = self.env['res.partner.bank'].create(bank_line_vals)
                    
                employee.update({
                    'address_home_id':  partner.id,
                    'bank_account_id':  bank_acc,
                })
            
                
        