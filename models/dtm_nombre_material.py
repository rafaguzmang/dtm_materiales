from odoo import models,fields

class NombreMaterial(models.Model):
    _name = "dtm.nombre.material"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Material')