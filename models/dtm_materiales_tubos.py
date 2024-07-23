from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re

class Tubos(models.Model):
    _name = "dtm.materiales.tubos"
    _description = "Sección para llevar el inventario de los tubos"
    _rec_name = "material_id"

    codigo = fields.Integer(string="ID", readonly=True)
    material_id = fields.Many2one("dtm.tubos.nombre",string="MATERIAL",required=True)
    calibre = fields.Float(string="Calibre")
    diametro = fields.Float(string="Diametro", store=True)
    largo = fields.Float(string="Largo")
    # area = fields.Float(string="Area")
    descripcion = fields.Text(string="Descripción")
    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )
    localizacion = fields.Char(string="Localización")

    def accion_guardar(self):
        if not self.descripcion:
            self.descripcion = ""
        get_info = self.env['dtm.materiales.tubos'].search([("material_id","=",self.material_id.id),("calibre","=",self.calibre),("largo","=",self.largo),("diametro","=",self.diametro)])
        if len(get_info)==1:
             # Agrega los materiales nuevo al modulo de diseño
            nombre = "Tubo " + self.material_id.nombre
            medida = str(self.largo) + " x " + str(self.diametro) + " @ " + str(self.calibre)
            get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
            if not get_diseno:
                get_id = self.env['dtm.diseno.almacen'].search([], order='id desc',limit=1)

                id = get_id.id + 1
                for result2 in range (1,get_id.id):
                    if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                        id = result2
                        break
                self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida, area,caracteristicas) VALUES ("+str(id)+","+str(self.disponible)+", '"+nombre+"', '"+medida+"',"+str(self.largo)+", '"+ self.descripcion + "')")
                get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
                self.codigo = get_diseno[0].id

            else:
                vals = {
                    "cantidad": self.cantidad - self.apartado,
                    "caracteristicas":self.descripcion
                }
                get_diseno.write(vals)
                get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
                self.codigo = get_diseno[0].id

             #Actualiza la lista de materiales de las OT
            # get_ot = self.env['dtm.materials.line'].search([("medida","=",get_diseno.medida),("nombre","=",get_diseno.nombre)])
            # # print(get_ot)
            # self.apartado = 0
            # self.disponible = self.cantidad
            # for item in get_ot:
            #     # print(item.materials_cuantity,item.materials_inventory,item.materials_required,self.disponible)
            #     if self.disponible <= 0:
            #         inventory = 0
            #         required = item.materials_cuantity
            #     elif self.disponible - item.materials_cuantity <= 0:
            #         inventory = self.disponible
            #         required = abs(self.disponible - item.materials_cuantity)
            #     elif item.materials_cuantity <= self.disponible:
            #         inventory = item.materials_cuantity
            #         required = 0
            #     self.apartado +=  item.materials_cuantity
            #     item.write({
            #         "materials_inventory":inventory,
            #         "materials_required":required,
            #     })
            #
            #     self.disponible = self.cantidad - self.apartado

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

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Tubos,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.tubos'].search([("codigo","=",False)])
        get_info.unlink()
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

    # def name_get(self):#--------------------------------Arreglo para cuando usa este modulo como Many2one--------------------
    #     res = []
    #     for result in self:
    #         res.append((result.id,f'{result.id}: {result.material_id.nombre} CALIBRE: {result.calibre_id.calibre} DIAMETRO: {result.diametro_id.diametro} LARGO:  {result.largo_id.largo}   '))
    #     return res

class NombreMaterial(models.Model):
    _name = "dtm.tubos.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Material')

class MaterialCalibre(models.Model):
    _name = "dtm.tubos.calibre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "calibre"

    calibre = fields.Char(string="Calibre")

class MaterialDiametro(models.Model):
    _name = "dtm.tubos.diametro"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "diametro"

    diametro = fields.Char(string="Diametro", default="0")

class MaterialLargo(models.Model):
    _name = "dtm.tubos.largo"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "largo"

    largo = fields.Char(string="Largo", default="0")


