# -*- coding: utf-8 -*-
{
    'name': "Timesheet Portal",

    'summary': """
    Timesheet Portal
        """,

    'description': """
        Timesheet Portal
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project/Timesheet',
    'version': '14.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['hr_timesheet','portal','analytic','approvals','de_employee_shift','resource',
        'web',
        'de_hr_attendance_report',        
        'rating',        
        'web_tour',
        'digest',
        'base',],

    'assets': {
        'web.assets_frontend': [
             'de_timesheet_portal/static/src/js/timesheet_portal.js',
        ]
    },
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/timesheet_report_wizard.xml',
        'report/hr_timesheet_report.xml',
        'report/hr_timesheet_template.xml',
        'views/hr_timesheet_type_views.xml',
        'views/hr_timesheet_views.xml',
        'views/timesheet_portal_templates.xml',
        
    ],
    
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
