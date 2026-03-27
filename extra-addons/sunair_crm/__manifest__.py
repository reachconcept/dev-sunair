# -*- coding: utf-8 -*-
{
    'name': 'Reach Concept : Module Name',
    'version': '19.0.1.0.0',
    'category': 'Business Management',
    'summary': """ Reach Concept : Module Name """,
    'description': """ Reach Concept : Module Name """,
    'author': 'Reach Concept',
    'company': 'Reach Concept',
    'maintainer': 'Reach Concept',
    'website': 'https://www.reachconcept.com',

    'depends': ['base','crm','mail'],

    'data': [
        "security/ir.model.access.csv",
        "views/customer_type_views.xml",
        "views/lead_type_views.xml",
        "views/crm_territory_views.xml",
        "views/crm_lead_views.xml",

    ],
    'assets': {
        'web.assets_backend': [
           
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}