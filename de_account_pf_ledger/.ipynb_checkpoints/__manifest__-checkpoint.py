# -*- coding: utf-8 -*-
{
    'name': "Account PF Ledger Report",

    'summary': """
        Account PF Ledger Report
        """,

    'description': """
        PF Ledger Report
        1- PF Ledger Form.
        2- PF Ledger Report.
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','hr_payroll','hr_work_entry_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/pf_ledger_wizard.xml',
        'report/pf_ledger_report.xml',
        'report/pf_ledger_report_template.xml',
        'views/partner_pf_ledger_views.xml',
        'views/pf_ledger_type_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
