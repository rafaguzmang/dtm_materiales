from odoo import api,fields,models
import re
class MaterialLargo(models.Model):
    _name = "dtm.largo.material"
    _rec_name = "largo"

    largo = fields.Char(string="Largo", defaul="0")