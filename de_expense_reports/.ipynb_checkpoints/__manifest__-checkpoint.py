# -*- coding: utf-8 -*-
{
    'name': "Expense Report",

    'summary': """
       Employees Payable, Advances Balance report required from Odoo. Attached please check required forma
       """,

    'description': """
        Employees Payable, Advances Balance report required from Odoo. Attached please check required forma
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['report_xlsx', 'base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/expense_report.xml',
        'wizard/employee_expense_wizard.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
