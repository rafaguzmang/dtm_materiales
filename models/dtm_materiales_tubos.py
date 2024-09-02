from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re

class Tubos(models.Model):
    _name = "dtm.materiales.tubos"
    _description = "Sección para llevar el inventario de los tubos"
    _rec_name = "material_id"

    codigo = fields.Integer(string="Código", readonly=True)
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
    user_almacen = fields.Boolean(compute="_compute_user_email_match")

    def _compute_user_email_match(self):
        for record in self:
            email = self.env.user.partner_id.email
            record.user_almacen = False
            if email in ["almacen@dtmindustry.com","rafaguzmang@hotmail.com"]:
                record.user_almacen = True

    def accion_guardar(self):
        get_almacen_codigo = self.env['dtm.diseno.almacen'].search([("id","=",self.codigo)])
        get_almacen_desc = self.env['dtm.diseno.almacen'].search([("nombre","=",f"Tubo {self.material_id.nombre}"),("medida","=",f"{self.largo} x {self.diametro} @ {self.calibre}")])
        vals = {
                    "cantidad": self.cantidad,
                    "apartado": self.apartado,
                    "disponible": self.disponible,
                    "area":self.largo
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
            nombre = f"Tubo {self.material_id.nombre}"
            medida = f"{self.largo} x {self.diametro} @ {self.calibre}"
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

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Tubos,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.tubos'].search([("codigo","=",False)])
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


