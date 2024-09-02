from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re

class Maquinados(models.Model):
    _name = "dtm.materiales.maquinados"
    _description = "Sección para llevar el inventario de los maquinados"
    _rec_name = "nombre_id"

    codigo = fields.Integer(string="Código", readonly=True)
    nombre_id = fields.Many2one("dtm.maquinados.nombre",string="NOMBRE",required=True)
    descripcion = fields.Text(string="DESCRIPCIÓN")
    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )
    localizacion = fields.Char(string="Localización")

    def accion_guardar(self):
        get_almacen_codigo = self.env['dtm.diseno.almacen'].search([("id","=",self.codigo)])
        get_almacen_desc = self.env['dtm.diseno.almacen'].search([("nombre","=",f"Maquinados {self.nombre_id.nombre}")])
        vals = {
                    "cantidad": self.cantidad,
                    "apartado": self.apartado,
                    "disponible": self.disponible,
                }
        if get_almacen_codigo or get_almacen_desc:
            get_almacen = get_almacen_codigo if get_almacen_codigo else get_almacen_desc
            self.codigo = get_almacen.id
            get_almacen.write(vals)
        else:
            for find_id in range(1,self.env['dtm.diseno.almacen'].search([], order='id desc', limit=1).id+1):
                if not self.env['dtm.diseno.almacen'].search([("id","=",find_id)]):
                    self.env.cr.execute(f"SELECT setval('dtm_diseno_almacen_id_seq', {find_id}, false);")
                    break
            nombre = f"Maquinados {self.nombre_id.nombre}"
            medida = ""
            vals["nombre"] = nombre
            vals["medida"] = medida
            get_almacen_codigo.create(vals)
            get_almacen = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
            self.codigo = get_almacen.id

            for find_id in range(1,self.env['dtm.diseno.almacen'].search([], order='id desc', limit=1).id+2):
                if not self.env['dtm.diseno.almacen'].search([("id","=",find_id)]):
                    self.env.cr.execute(f"SELECT setval('dtm_diseno_almacen_id_seq', {find_id}, false);")
                    break


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

    # def name_get(self):#--------------------------------Arreglo para cuando usa este modulo como Many2one--------------------
    #     res = []
    #     for result in self:
    #         res.append((result.id,f'{result.id}: {result.nombre_id.nombre} '))
    #     return res

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Maquinados,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.maquinados'].search([("codigo","=",False)])
        get_info.unlink()
        return res


class NombreOtros(models.Model):
    _name = "dtm.maquinados.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Nombre')

