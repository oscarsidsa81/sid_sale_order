from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # 1. x_costes – tipo: Monetario
    x_costes = fields.Monetary (
        string="Costes adicionales",
        currency_field='currency_id',
        store=True,
        copy=True
    )

    # 2. x_dossier – tipo: Booleano
    x_dossier = fields.Boolean (
        string="Tiene Dossier",
        help="Campo para saber si se creó un dossier para este nº de contrato",
        store=True
    )

    # 3. x_invoice_out – tipo: Booleano
    x_invoice_out = fields.Boolean (
        string="Facturado en otra factura",
        help="Campo ayuda",
        store=True
    )

    # 4. x_margen – tipo: Float (número flotante calculado)
    x_margen = fields.Float (
        string="Margen revisado",
        compute="_compute_x_margen",
        store=True,
        readonly=True,
        tracking=1
    )

    # 5. x_sale_order_id_sale_activity_count – tipo: Entero (calculado)
    x_sale_order_id_sale_activity_count = fields.Integer (
        string="Sale order count in Activities",
        compute="_compute_sale_activity_count",
        store=True
    )

    x_aval = fields.Boolean(
        string="Avales",
        tracking=1,
        store=True
    )

    x_restante = fields.Monetary(
        string="Restante",
        compute="_compute_x_restante",
        help="Base imponible que queda por entregar",
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    x_excesos = fields.Monetary(
        string="Excesos Pend.",
        compute="_compute_x_excesos",
        store=True,
        readonly=True,
        currency_field='currency_id',
        help="Para cálculo de excesos de metraje",
    )

    x_hitos_pendientes = fields.Monetary(
        string="Hitos pendientes",
        compute="_compute_x_hitos_pendientes",
        store=True,
        currency_field='currency_id',
        help="Para cálculo de Hitos Pendientes del campo Down Payment"
    )

    x_pendiente = fields.Monetary(
        string="Base Pendiente",
        compute="_compute_x_pendiente",
        help="Base imponible que queda por facturar y ya está entregado",
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    x_total = fields.Monetary(
        string="Base Total Facturada",
        compute="_compute_x_total",
        help="Base facturada por línea de venta",
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    # === MÉTODOS ===

    @api.depends('order_line.qty_delivered', 'order_line.price_reduce', 'order_line.product_uom_qty', 'order_line.product_id')
    def _compute_x_restante(self):
        for record in self:
            total_base = 0.0
            for line in record.order_line:
                if line.product_id.default_code != "Down payment":
                    if line.qty_delivered < line.product_uom_qty:
                        total_base += (line.product_uom_qty - line.qty_delivered) * line.price_reduce
            record.x_restante = total_base

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

    @api.depends('order_line.product_id', 'order_line.product_uom_qty', 'order_line.qty_delivered', 'order_line.qty_invoiced')
    def _compute_x_hitos_pendientes(self):
        for record in self:
            total_down_payment = 0.0
            for line in record.order_line:
                if line.product_id.default_code == "Down payment" and line.product_uom_qty > 0 and line.qty_delivered == 0 and line.qty_invoiced == 0:
                    total_down_payment += (line.product_uom_qty - line.qty_delivered) * line.price_reduce
            record.x_hitos_pendientes = total_down_payment

    @api.depends('order_line.qty_to_invoice', 'order_line.price_reduce', 'invoice_ids', 'order_line.qty_delivered', 'order_line.product_uom_qty', 'order_line.qty_invoiced', 'order_line.product_id')
    def _compute_x_pendiente(self):
        for record in self:
            total_base_ex = 0.0
            for line in record.order_line:
                if line.product_id.default_code != "Down payment":
                    if line.qty_delivered > line.product_uom_qty and line.qty_invoiced <= line.product_uom_qty:
                        total_base_ex += (line.qty_delivered - line.product_uom_qty) * line.price_reduce
                    elif line.qty_invoiced < line.qty_delivered and line.qty_invoiced > line.product_uom_qty:
                        total_base_ex += (line.qty_delivered - line.qty_invoiced) * line.price_reduce
            total_base = 0.0
            for line in record.order_line:
                total_base += line.qty_to_invoice * line.price_reduce
            record.x_pendiente = total_base - total_base_ex

    @api.depends('order_line.qty_invoiced', 'order_line.price_reduce_taxexcl')
    def _compute_x_total(self):
        for record in self:
            total_base = 0.0
            for line in record.order_line:
                total_base += line.qty_invoiced * line.price_reduce_taxexcl
            record.x_total = total_base

    @api.depends ( 'margin', 'x_costes', 'amount_untaxed', 'margin_percent' )
    def _compute_x_margen(self) :
        for record in self :
            if record.x_costes > 0 :
                try :
                    record.x_margen = (record.margin - record.x_costes) / record.amount_untaxed
                except ZeroDivisionError :
                    record.x_margen = 0
            else :
                record.x_margen = record.margin_percent

    @api.depends ( 'activity_ids' )
    def _compute_sale_activity_count(self) :
        for record in self :
            record.x_sale_order_id_sale_activity_count = self.env['sale.activity'].search_count ( [
                ('sale_order_id', '=', record.id)
            ] )