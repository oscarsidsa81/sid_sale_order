from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_restante = fields.Monetary(
        string="Restante",
        compute="_compute_x_restante",
        help="Base imponible que queda por entregar",
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    @api.depends('order_line.qty_delivered', 'order_line.price_reduce', 'order_line.product_uom_qty',
                 'order_line.product_id')
    def _compute_x_restante(self):
        for record in self:
            total_base = 0.0
            for line in record.order_line:
                if line.product_id.default_code != "Down payment":
                    if line.qty_delivered < line.product_uom_qty:
                        total_base += (line.product_uom_qty - line.qty_delivered) * line.price_reduce
            record.x_restante = total_base
