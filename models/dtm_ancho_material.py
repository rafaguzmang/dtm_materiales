from odoo import fields,models
import re

class MaterialAncho(models.Model):
    _name = "dtm.ancho.material"
    _rec_name = "ancho"

    ancho = fields.Char(string="Ancho", default="0")