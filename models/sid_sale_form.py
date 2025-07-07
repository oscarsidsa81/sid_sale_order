from odoo import fields, models, api

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    x_aval = fields.Boolean(
        string="Avales",
        tracking=1,
        store=True
    )
