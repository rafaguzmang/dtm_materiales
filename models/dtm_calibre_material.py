from odoo import fields,models


class MaterialCalibre(models.Model):
    _name = "dtm.calibre.material"
    _rec_name = "calibre"

    calibre = fields.Char(string="Calibre")