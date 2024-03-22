from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re

class Rodamientos(models.Model):
    _name = "dtm.materiales.rodamientos"
    _description = "Sección para llevar el inventario de los rodamientos"
    _rec_name = "material_id"

    material_id = fields.Many2one("dtm.rodamientos.nombre",string="Nombre",required=True)
    descripcion = fields.Text(string="Descripción")
    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )

    def write(self,vals):
        res = super(Rodamientos,self).write(vals)
        nombre = "Rodamientos "+self.material_id.nombre
        get_info = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre)])


        descripcion = ""
        if self.descripcion:
            descripcion = self.descripcion

        if get_info:
            # print("existe")
            # print(self.disponible,self.area,descripcion,nombre,medida)
            self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(self.disponible)+", caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' ")
        else:
            # print("no existe")
            # print(nombre,medida,self.largo,self.disponible)
            get_id = self.env['dtm.diseno.almacen'].search_count([])
            for result2 in range (1,get_id+1):
                if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                    id = result2
                    break
            self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, caracteristicas) VALUES ("+str(id)+","+str(self.disponible)+", '"+nombre+"', '"+ descripcion+ "')")

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

    @api.model
    def create (self,vals):
        res = super(Rodamientos, self).create(vals)
        get_info = self.env['dtm.materiales.rodamientos'].search([])

        mapa ={}
        for get in get_info:
            material_id = get.material_id

            if mapa.get(material_id):
                self.env.cr.execute("DELETE FROM dtm_materiales_rodamientos WHERE id="+str(get.id))
                raise ValidationError("Material Duplicado")
            else:
                mapa[material_id] = 1
        return res

    # def material_cantidad(self,modelo):
    #     get_mater = self.env['dtm.materials.line'].search([])
    #     for get in get_mater:
    #          if get:
    #             nombre = str(get.materials_list.nombre)
    #             if re.match(".*[Rr][oO][dD][aA][mM][iI][eE][nN][tT][oO].*",nombre):
    #                 nombre = re.sub("^\s+","",nombre)
    #                 nombre = nombre[nombre.index(" "):]
    #                 nombre = re.sub("^\s+","",nombre)
    #                 nombre = re.sub("\s+$","",nombre)
    #                 # print("result 1",nombre,medida)
    #                 # Busca coincidencias entre el almacen y el aréa de diseno dtm_diseno_almacen
    #                 get_mid = self.env['dtm.rodamientos.nombre'].search([("nombre","=",nombre)]).id
    #                 get_angulo = self.env['dtm.materiales.rodamientos'].search([("material_id","=",get_mid)])
    #                 # print(get_mid,nombre,get_angulo)
    #                 if get_angulo:
    #                     suma = 0
    #                     # print(get.materials_list.nombre,get.materials_list.medida)
    #                     get_cant = self.env['dtm.materials.line'].search([("nombre","=",get.materials_list.nombre)])
    #                     # print(get_cant)
    #                     for cant in get_cant:
    #                         suma += cant.materials_cuantity
    #                     return (suma,get_angulo.id)

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Rodamientos,self).get_view(view_id, view_type,**options)

        get_info = self.env['dtm.materiales.rodamientos'].search([])

        mapa ={}
        for get in get_info:
            material_id = get.material_id

            if mapa.get(material_id):
                self.env.cr.execute("DELETE FROM dtm_materiales_rodamientos WHERE id="+str(get.id))
            else:
                mapa[material_id] = 1

            nombre = "Rodamientos "+get.material_id.nombre
            get_info = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre)])
            if not get.descripcion:
                descripcion = ""
            else:
                descripcion = get.descripcion

            if get_info:
                self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(get.disponible)+",  caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' ")
            else:
                # print(nombre,medida)
                get_id = self.env['dtm.diseno.almacen'].search_count([])
                for result2 in range (1,get_id+1):
                    if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                        id = result2
                        break
                self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, caracteristicas) VALUES ("+str(id)+","+str(get.disponible)+", '"+nombre+"', '"+ descripcion+ "')")

        return res

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
            res.append((result.id,f'{result.id}: {result.material_id.nombre}  DESCRIPCIÓN {result.descripcion}   '))
        return res

class NombreMaterial(models.Model):
    _name = "dtm.rodamientos.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Material')




