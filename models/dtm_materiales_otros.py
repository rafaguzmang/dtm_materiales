from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re

class Otros(models.Model):
    _name = "dtm.materiales.otros"
    _description = "Sección para llevar el inventario de los otros"
    _rec_name = "nombre_id"

    nombre_id = fields.Many2one("dtm.otros.nombre",string="NOMBRE",required=True)
    descripcion = fields.Text(string="DESCRIPCIÓN")

    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )

    def write(self,vals):
        res = super(Otros,self).write(vals)
        nombre = self.nombre_id.nombre
        get_info = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre)])

        descripcion = ""
        if self.descripcion:
            descripcion = self.descripcion

        if get_info:
            # print("existe")
            # print(self.disponible,self.area,descripcion,nombre)
            self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(self.disponible)+",  caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' ")
        else:

            get_id = self.env['dtm.diseno.almacen'].search_count([])
            for result2 in range (1,get_id+1):
                if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                    id = result2
                    break
            self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, caracteristicas) VALUES ("+str(id)+","+str(self.disponible)+", '"+nombre+"', '"+descripcion+ "')")
        return res

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
        res = super(Otros, self).create(vals)
        get_info = self.env['dtm.materiales.otros'].search([])

        mapa ={}
        for get in get_info:
            nombre_id = get.nombre_id.nombre
            if mapa.get(nombre_id):
                self.env.cr.execute("DELETE FROM dtm_materiales_otros WHERE id="+str(get.id))
                raise ValidationError("Material Duplicado")
            else:
                mapa[nombre_id] = 1


        return res

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Otros,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.otros'].search([])

        mapa ={}
        for get in get_info:
            nombre_id = get.nombre_id.nombre

            if mapa.get(nombre_id):
                self.env.cr.execute("DELETE FROM dtm_materiales_otros WHERE id="+str(get.id))
            else:
                mapa[nombre_id] = 1
            #Inserta el nuevo material en el modulo de dtm_diseno_almacen
            nombre = get.nombre_id.nombre
            get_esp = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre)])
            if not get.descripcion:
                descripcion = ""
            else:
                descripcion = get.descripcion
            if get_esp:
                self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(get.disponible)+", caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"'")
            else:
                # print(nombre,medida)
                get_id = self.env['dtm.diseno.almacen'].search_count([])
                for result2 in range (1,get_id+1):
                    if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                        id = result2
                        break
                self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, caracteristicas) VALUES ("+str(id)+","+str(get.disponible)+", '"+nombre+"', '"+ descripcion+ "')")

        return res


class NombreOtros(models.Model):
    _name = "dtm.otros.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Nombre')

