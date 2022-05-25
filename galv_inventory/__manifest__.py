{
    'name': "Galv Inventory",
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
    'depends': ['base', 'purchase', 'account', 'hr', 'galvanization_inventory', 'stock','product'],
    "images": ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        'data/check.xml',
        'views/employee_requisition.xml',
        'views/issue_form.xml',
        'views/product_report.xml',
        'report/report.xml',
        'report/purchase_report.xml',
        'report/issue_report.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}