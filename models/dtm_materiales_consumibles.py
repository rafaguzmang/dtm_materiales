from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re

class Consumibles(models.Model):
    _name = "dtm.materiales.consumibles"
    _description = "Sección para llevar el inventario de los consumibles"
    _rec_name = "nombre_id"

    nombre_id = fields.Many2one("dtm.consumibles.nombre",string="NOMBRE",required=True)
    descripcion = fields.Text(string="DESCRIPCIÓN")
    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    localizacion = fields.Char(string="Localización")

    @api.onchange("entradas")#---------------------------Suma material nuevo------------------------------------------
    def _anchange_cantidad(self):
        # print(self.cantidad)
        self.cantidad += self.entradas

    def accion_salidas(self):#-----------------Resta una unidad al stock----------------------------------------------
         if self.cantidad <= 0:
            self.cantidad = 0
         else:
            self.cantidad -= 1

    def accion_guardar(self):
        if not self.descripcion:
            self.descripcion = ""
        get_info = self.env['dtm.materiales.consumibles'].search([("nombre_id","=",self.nombre_id.id)])
        if len(get_info)>1:
            raise ValidationError("Material Duplicado")

class NombreMaterial(models.Model):
    _name = "dtm.consumibles.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Nombre')

