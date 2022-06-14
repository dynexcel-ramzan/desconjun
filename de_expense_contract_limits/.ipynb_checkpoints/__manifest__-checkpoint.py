# -*- coding: utf-8 -*-
{
    'name': "Expense Contract Limits",

    'summary': """
        Expense Contract Limits
        """,

    'description': """
        Expense Contract Limits
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Contract',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant','de_employee_shift','de_employee_overtime'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/shift_replace_wizard.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
