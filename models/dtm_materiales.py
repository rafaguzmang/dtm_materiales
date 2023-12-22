from odoo import api,models,fields

class Materiales(models.Model):
    _name = "dtm.materiales"

   
    material_id = fields.Many2one("dtm.nombre.material",string="MATERIAL")
    calibre_id = fields.Many2one("dtm.calibre.material",string="CALIBRE")
    largo_id = fields.Many2one("dtm.largo.material",string="LARGO", default="0")
    ancho_id = fields.Many2one("dtm.ancho.material",string="ANCHO", default="0")
    descripcion = fields.Text(string="Descripción")
    entradas = fields.Integer(string="Entradas")
    salidas = fields.Integer(string="Salidas")
    cantidad = fields.Integer(string="Stock")
    
    @api.onchange("entradas")
    def _onchange_entradas(self):
        for record in self:
            record.cantidad += record.entradas
            record.cantidad = 0

    def accion_salidas(self):
        for record in self:
            record.cantidad -= record.salidas
            record.salidas = 0








   
        
        

            
        


