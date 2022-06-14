# -*- coding: utf-8 -*-
{
    'name': "Modification",

    'summary': """
            Sale Modification and basic control
        """,

    'description': """
        Modification
        1- Sale order.
        2- Partner.
        3- Product.
    """,

    'author': "Emplois Career",
    'website': "https://emploiscareer.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Basic',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','product','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_data.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
