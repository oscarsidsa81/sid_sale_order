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

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_excesos = fields.Monetary(
        string="Excesos Pend.",
        compute="_compute_x_excesos",
        store=True,
        readonly=True,
        currency_field='currency_id',
        help="Para cálculo de excesos de metraje",
    )

    @api.depends('order_line.qty_delivered', 'order_line.qty_invoiced', 'order_line.price_reduce',
                 'order_line.product_uom_qty', 'order_line.product_id')
    def _compute_x_excesos(self):
        for record in self:
            total_base = 0.0
            for line in record.order_line:
                if line.product_id.default_code != "Down payment":
                    if line.qty_delivered > line.product_uom_qty and line.qty_invoiced <= line.product_uom_qty:
                        total_base += (line.qty_delivered - line.product_uom_qty) * line.price_reduce
                    elif line.qty_invoiced < line.qty_delivered and line.qty_invoiced > line.product_uom_qty:
                        total_base += (line.qty_delivered - line.qty_invoiced) * line.price_reduce
            record.x_excesos = total_base

    class SaleOrder(models.Model):
            _inherit = 'sale.order'

            x_hitos_pendientes = fields.Monetary(
                string="Hitos pendientes",
                compute="_compute_x_hitos_pendientes",
                store=True,
                currency_field='currency_id',
                help="Para cálculo de Hitos Pendientes del campo Down Payment"
            )

    def _compute_x_hitos_pendientes(self):
        for record in self:
            total_down_payment = 0.0  # Inicializamos la variable para sumar las líneas con producto 10987
            for line in record.order_line:
                # Si el producto es 10987, la cantidad es mayor que 0 y no está facturado
                if line.product_id.default_code == "Down payment" and line.product_uom_qty > 0 and line.qty_delivered == 0 and line.qty_invoiced == 0:
                    total_down_payment += (line.product_uom_qty - line.qty_delivered) * line.price_reduce
            # Asignamos el valor calculado al campo 'x_hitos'
            record.write({'x_hitos_pendientes': total_down_payment})

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_pendiente = fields.Monetary(
        string="Base Pendiente",
        compute="_compute_x_pendiente",
        help="Base imponible que queda por facturar y ya está entregado",
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    @api.depends('order_line.qty_to_invoice', 'order_line.price_reduce', 'invoice_ids', 'order_line.qty_delivered', 'order_line.product_uom_qty')

    def _compute_x_pendiente(self):
        for record in self:
            total_base_ex = 0.0
            for line in record.order_line:
                # Verificamos si el producto tiene un ID diferente de 10987
                if line.product_id.default_code != "Down payment":
                    # Si la cantidad entregada es mayor que la cantidad pedida, restamos la diferencia
                    if line.qty_delivered > line.product_uom_qty and line.qty_invoiced <= line.product_uom_qty:
                        total_base_ex += (line.qty_delivered - line.product_uom_qty) * line.price_reduce
                        # Si la cantidad facturada es mayor que la cantidad pedida, restamos la diferencia
                    elif line.qty_invoiced < line.qty_delivered and line.qty_invoiced > line.product_uom_qty:
                        total_base_ex += (line.qty_delivered - line.qty_invoiced) * line.price_reduce
                        # En caso contrario, no se suma nada
                    else:
                        total_base_ex += 0.0
            total_base = 0.0
            for line in record.order_line:
                total_base += line.qty_to_invoice * line.price_reduce
            record.write({'x_pendiente': total_base - total_base_ex})