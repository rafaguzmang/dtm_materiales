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
        if not self.descripcion:
            self.descripcion = ""
        get_info = self.env['dtm.materiales.maquinados'].search([("nombre_id","=",self.nombre_id.id)])
        if len(get_info)==1:
             # Agrega los materiales nuevo al modulo de diseño
            nombre = f"Maquinados {self.nombre_id.nombre}"
            medida = ""
            get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("caracteristicas","=",self.descripcion)])
            if not get_diseno:
                get_id = self.env['dtm.diseno.almacen'].search([], order='id desc',limit=1)

                id = get_id.id + 1
                for result2 in range (1,get_id.id):
                    if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                        id = result2
                        break
                self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida,caracteristicas) VALUES ("+str(id)+","+str(self.disponible)+", '"+nombre+"', '"+medida+"', '"+ self.descripcion + "')")
                get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("caracteristicas","=",self.descripcion)])
                self.codigo = get_diseno[0].id
            else:
                vals = {
                    "cantidad": self.cantidad - self.apartado,
                    "caracteristicas":self.descripcion
                }
                get_diseno.write(vals)
                get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("caracteristicas","=",self.descripcion)])
                self.codigo = get_diseno[0].id

        elif len(get_info)>1:
            raise ValidationError("Material Duplicado")


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

