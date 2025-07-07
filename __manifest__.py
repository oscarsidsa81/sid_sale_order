{
    'name': 'sid_sale_order',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Funcionalidades varias',
    'description': 'Módulo con todas las funcionalidades de v15 personalizadas',
    'author': 'oscarsidsa81',
    'depends': ['base','sale_management','product','oct_fecha_contrato_ventas','account','account_accountant','documents','stock','web_studio','purchase'],
    'data': [
        'views/sid_sale_order.xml'
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}