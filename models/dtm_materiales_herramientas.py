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

    def accion_proyecto(self):
        if self.apartado <= 0:
            self.apartado = 0
        else:
            self.apartado -= 1
        if self.cantidad <= 0:
            self.cantidad = 0
        else:
            self.cantidad -= 1

    @api.onchange("entradas")#---------------------------Suma material nuevo------------------------------------------
    def _anchange_cantidad(self):
        # print(self.cantidad)
        self.cantidad += self.entradas

    def accion_salidas(self):#-----------------Resta una unidad al stock----------------------------------------------
        # print(self.cantidad)
         if self.cantidad <= 0:
            self.cantidad = 0
         else:
            self.cantidad -= 1

    def _compute_disponible(self):#-----------------------------Saca la cantidad del material que hay disponible---------------
        for result in self:
            result.disponible = result.cantidad - result.apartado

    def name_get(self):#--------------------------------Arreglo para cuando usa este modulo como Many2one--------------------
        res = []
        for result in self:
            res.append((result.id,f'{result.id}: {result.nombre_id.nombre} '))
        return res

    @api.model
    def create (self,vals):
        res = super(Herramientas, self).create(vals)
        get_info = self.env['dtm.materiales.herramientas'].search([])

        mapa ={}
        for get in get_info:
            nombre_id = get.nombre_id.nombre


            if mapa.get(nombre_id):
                self.env.cr.execute("DELETE FROM dtm_materiales_herramientas WHERE id="+str(get.id))
                raise ValidationError("Material Duplicado")
            else:
                mapa[nombre_id] = 1

        return res

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Herramientas,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.herramientas'].search([])

        mapa ={}
        for get in get_info:
            nombre_id = get.nombre_id.nombre

            if mapa.get(nombre_id):
                self.env.cr.execute("DELETE FROM dtm_materiales_herramientas WHERE id="+str(get.id))

            else:
                mapa[nombre_id] = 1
        return res


class NombreHerramientas(models.Model):
    _name = "dtm.herramientas.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Nombre')

