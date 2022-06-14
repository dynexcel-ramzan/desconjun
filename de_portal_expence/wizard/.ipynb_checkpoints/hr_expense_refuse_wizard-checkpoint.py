from odoo import models, fields, api, _



class HrExpenseRefuseWizard(models.TransientModel):
    _inherit = "hr.expense.refuse.wizard"
    
    
    def expense_refuse_reason(self):
        self.ensure_one()
        if self.hr_expense_ids:
            self.hr_expense_ids.refuse_expense(self.reason)
        if self.hr_expense_sheet_id:
            self.hr_expense_sheet_id.refuse_sheet(self.reason)
            self.hr_expense_sheet_id.update({
                'reason': self.reason, 
            })
        return {'type': 'ir.actions.act_window_close'}
    