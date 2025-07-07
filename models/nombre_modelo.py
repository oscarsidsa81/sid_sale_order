from odoo import models, fields

class NombreModelo(models.Model):
    _name = 'mi_modulo.nombre_modelo'
    _description = 'Nombre del modelo'

    name = fields.Char(string="Nombre")
