# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    vehicle_meter_line_ids = fields.One2many('vehicle.meter.reading', 'employee_id', string='Vehicle Meter Line')
    vehicle_id = fields.Many2one('vehicle.meter.detail', string='Vehicle')
    expense_incharge_id = fields.Many2one('hr.employee', string='Expense Incharge')
    
    
    @api.constrains('name')
    def _check_partner_name(self):
        for line in self:
            if not line.address_home_id:
                vals = {
                    'company_type': 'person',
                    'name': line.name,
                    'street': line.temporary_address,
                    'email':  line.work_email,
                    'company_id': line.company_id.id, 
                }
                partner = self.env['res.partner'].create(vals)
                line.update({
                    'address_home_id': partner.id,
                })

            
    @api.constrains('vehicle_id')
    def _check_vehicle(self):
        for line in self:
            if line.vehicle_id and not line.vehicle_meter_line_ids:
                vehicle_products = self.env['expense.sub.category'].search([('ora_unit','=','km')])
                for vehicle_prd in vehicle_products:
                    vehicle_meter_vals = {
                        'sub_category_id':  vehicle_prd.id,
                        'limit_reading':  vehicle_prd.meter_reading,
                        'opening_reading':  0,
                        'ora_unit':  vehicle_prd.ora_unit,
                        'employee_id': line.id
                    }
                    meter_reading=self.env['vehicle.meter.reading'].create(vehicle_meter_vals)
                

class MedicalReading(models.Model):
    _name='medical.reading'
    
class VehicleMeterLine(models.Model):
    _name = 'vehicle.meter.reading'
    _description= 'Vehicle Meter Reading'
    
    sub_category_id = fields.Many2one('expense.sub.category', required=True, string='Type', domain="[('ora_unit','=', 'km')]")
    limit_reading = fields.Float(related='sub_category_id.meter_reading', string='Limit')
    opening_reading = fields.Integer(string='Last Reading')
    ora_unit = fields.Selection(related='sub_category_id.ora_unit', string='Unit')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    
    
    