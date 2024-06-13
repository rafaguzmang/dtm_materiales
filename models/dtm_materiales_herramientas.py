from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re

class Herramientas(models.Model):
    _name = "dtm.materiales.herramientas"
    _description = "Sección para llevar el inventario de los herramientas"
    _rec_name = "nombre_id"

    nombre_id = fields.Many2one("dtm.herramientas.nombre",string="NOMBRE",required=True)
    descripcion = fields.Text(string="DESCRIPCIÓN")

    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )
    localizacion = fields.Char(string="Localización")

    @api.onchange("entradas")#---------------------------Suma material nuevo------------------------------------------
    def _anchange_cantidad(self):
        self.cantidad += self.entradas

    def accion_salidas(self):#-----------------Resta una unidad al stock----------------------------------------------
         if self.cantidad <= 0:
            self.cantidad = 0
         else:
            self.cantidad -= 1

    def accion_guardar(self):
        get_info = self.env['dtm.materiales.herramientas'].search([("nombre_id","=",self.nombre_id.id)])
        if len(get_info)>1:
            raise ValidationError("Material Duplicado")


class NombreHerramientas(models.Model):
    _name = "dtm.herramientas.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Nombre')

