# -*- coding: utf-8 -*-
{
    'name': 'Reach Concept : Sunair Shades Structure',
    'version': '19.0.1.0.0',
    'category': 'Business Management',
    'summary': """ Reach Concept : Sunair Shades Structure """,
    'description': """ Reach Concept : Sunair Shades Structure """,
    'author': 'Reach Concept',
    'company': 'Reach Concept',
    'maintainer': 'Reach Concept',
    'website': 'https://www.reachconcept.com',

    'depends': ['base','crm','mail','sale'],

    'data': [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/customer_type_views.xml",
        "views/lead_type_views.xml",
        "views/crm_territory_views.xml",
        "views/crm_lead_views.xml",
        "views/crm_application_views.xml",
        "views/sunair_dashboard.xml",
        "views/crm_lead2opportunity_partner.xml",
        "views/res_partner_view.xml",
        "views/product_views.xml",
        "views/crm_product_category_views.xml",

    ],
    'assets': {
        'web.assets_backend': [
           'sunair_crm/static/src/js/dashboard.js',
           'sunair_crm/static/src/xml/dashboard.xml',
           'sunair_crm/static/src/css/dashboard.css',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}