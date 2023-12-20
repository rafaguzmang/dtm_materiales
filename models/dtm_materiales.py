from odoo import api,models,fields

class Materiales(models.Model):
    _name = "dtm.materiales"

   
    material_id = fields.Many2one("dtm.nombre.material",string="MATERIAL")
    calibre_id = fields.Many2one("dtm.calibre.material",string="CALIBRE")
    largo_id = fields.Many2one("dtm.largo.material",string="LARGO", default="0")
    ancho_id = fields.Many2one("dtm.ancho.material",string="ANCHO", default="0")
    cantidad = fields.Integer(string="CANTIDAD")

   
        
        

            
        


