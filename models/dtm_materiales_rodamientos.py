from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re

class Rodamientos(models.Model):
    _name = "dtm.materiales.rodamientos"
    _description = "Sección para llevar el inventario de los rodamientos"
    _rec_name = "material_id"

    codigo = fields.Integer(string="ID", readonly=True)
    material_id = fields.Many2one("dtm.rodamientos.nombre",string="Nombre",required=True)
    descripcion = fields.Text(string="Descripción")
    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )
    localizacion = fields.Char(string="Localización")
    user_almacen = fields.Boolean(compute="_compute_user_email_match")

    def _compute_user_email_match(self):
        for record in self:
            email = self.env.user.partner_id.email
            record.user_almacen = False
            if email in ["almacen@dtmindustry.com","rafaguzmang@hotmail.com"]:
                record.user_almacen = True

    def accion_proyecto(self):
        email = self.env.user.partner_id.email
        if email in ["almacen@dtmindustry.com","rafaguzmang@hotmail.com"]:
            if self.apartado <= 0:
                self.apartado = 0
            else:
                self.apartado -= 1
            if self.cantidad <= 0:
                self.cantidad = 0
            else:
                self.cantidad -= 1

    def accion_guardar(self):
        email = self.env.user.partner_id.email
        if not self.descripcion:
            self.descripcion = ""
        get_info = self.env['dtm.materiales.rodamientos'].search([("material_id","=",self.material_id.id)])
        if  len(get_info)==1:
            nombre = "Rodamientos " + self.material_id.nombre
            medida = ""
            get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
            if not get_diseno:
                get_id = self.env['dtm.diseno.almacen'].search([], order='id desc',limit=1)

                id = get_id.id + 1
                for result2 in range (1,get_id.id):
                    if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                        id = result2
                        break
                cantidad = 0
                if email in ["almacen@dtmindustry.com","rafaguzmang@hotmail.com"]:
                    cantidad = self.disponible
                self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida, caracteristicas) VALUES ("+str(id)+","+str(cantidad)+", '"+nombre+"', '"+medida+"', '"+ self.descripcion + "')")
                get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
                self.codigo = get_diseno[0].id

            elif email in ["almacen@dtmindustry.com","rafaguzmang@hotmail.com"]:
                vals = {
                    "cantidad": self.cantidad - self.apartado,
                    "caracteristicas":self.descripcion
                }
                get_diseno.write(vals)
                get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
                self.codigo = get_diseno[0].id
        elif len(get_info)>1:
            raise ValidationError("Material Duplicado")
        self.entradas = 0

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Rodamientos,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.rodamientos'].search([("codigo","=",False)])
        get_info.unlink()

        email = self.env.user.partner_id.email
        self.user_almacen = False
        if email in ["almacen@dtmindustry.com","rafaguzmang@hotmail.com"]:
            self.user_almacen = True
        return res

    @api.onchange("entradas")#---------------------------Suma material nuevo------------------------------------------
    def _anchange_cantidad(self):
        email = self.env.user.partner_id.email
        if email in ["almacen@dtmindustry.com","rafaguzmang@hotmail.com"]:
            self.cantidad += self.entradas

    def accion_salidas(self):#-----------------Resta una unidad al stock----------------------------------------------
        email = self.env.user.partner_id.email
        if email in ["almacen@dtmindustry.com","rafaguzmang@hotmail.com"]:
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
    #         res.append((result.id,f'{result.id}: {result.material_id.nombre}  DESCRIPCIÓN {result.descripcion}   '))
    #     return res

class NombreMaterial(models.Model):
    _name = "dtm.rodamientos.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Material')




