{
    'name': "Galvanization Inventory",
    'author':
        'Enzapps',
    'summary': """
    New module for Galvanization Inventory
""",

    'description': """
    New module for Galvanization Inventory
    """,
    'website': "",
    'category': 'base',
    'version': '14.0',
    'depends': ['base', 'purchase', 'account', 'hr', 'stock'],
    "images": ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_inherit.xml',
        'views/purchase_report.xml',
        # 'report/report.xml',
        # 'report/purchase_report.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}