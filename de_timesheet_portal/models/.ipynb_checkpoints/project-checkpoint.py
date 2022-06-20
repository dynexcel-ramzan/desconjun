# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def get_website_sale_projects(self):
        return self.sudo().search([])

    def get_website_sale_tasks(self):
        return self.sudo().task_ids
