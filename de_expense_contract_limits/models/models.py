# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    expense_percent = fields.Float(string='Salary(%) Expense Limit(Contract)')
    expense_amt_limit = fields.Float(string='Expense Amount Limit(Contract)')



class AccountChangeLockDate(models.TransientModel):
    """
    This wizard is used to change the lock date
    """
    _inherit = 'account.change.lock.date'

    def change_lock_date(self):
        if self.user_has_groups('de_expense_contract_limits.group_unlock_date_ora'):
            self.env.company.sudo().write({
                'period_lock_date': self.period_lock_date,
                'fiscalyear_lock_date': self.fiscalyear_lock_date,
                'tax_lock_date': self.tax_lock_date,
            })
        elif self.user_has_groups('account.group_account_manager'):
            if self.env.company.period_lock_date > self.period_lock_date or self.env.company.fiscalyear_lock_date > self.fiscalyear_lock_date or self.env.company.tax_lock_date > self.tax_lock_date:
                raise UserError(_('You Are not Allow to Un-lock dates!')) 
            else:
                self.env.company.sudo().write({
                   'period_lock_date': self.period_lock_date,
                   'fiscalyear_lock_date': self.fiscalyear_lock_date,
                   'tax_lock_date': self.tax_lock_date,
                })
        else:
            raise UserError(_('Only Billing Administrators are allowed to change lock dates!'))
        return {'type': 'ir.actions.act_window_close'}
 

    

