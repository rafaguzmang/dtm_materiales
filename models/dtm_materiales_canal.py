from odoo import api,models,fields
from odoo.exceptions import ValidationError
import re

class Canal(models.Model):
    _name = "dtm.materiales.canal"
    _description = "Sección para llevar el inventario de las canal"
    _rec_name = "material_id"

    codigo = fields.Integer(string="Código", readonly=True)
    material_id = fields.Many2one("dtm.canal.nombre",string="MATERIAL",required=True)
    espesor = fields.Float(string="Espesor")
    ancho = fields.Float(string="Ancho")
    alto = fields.Float(string="Alto", compute="_compute_alto_id", store=True)
    largo = fields.Float(string="Largo")
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
        get_almacen = self.env['dtm.diseno.almacen'].browse(self.codigo)
        vals = {
                    "cantidad": self.cantidad,
                    "apartado": self.apartado,
                    "disponible": self.disponible,
                    "area":self.largo
                }
        if get_almacen:
            get_almacen.write(vals)
        else:
            for find_id in range(1,self.env['dtm.diseno.almacen'].search([], order='id desc', limit=1).id+1):
                if not self.env['dtm.diseno.almacen'].search([("id","=",find_id)]):
                    self.env.cr.execute(f"SELECT setval('dtm_diseno_almacen_id_seq', {find_id}, false);")
                    break
            nombre = f"Canal {self.material_id.nombre}"
            medida = f"{self.alto} x {self.ancho} espesor {self.espesor}, {self.largo}"
            vals["nombre"] = nombre
            vals["medida"] = medida
            get_almacen.create(vals)
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
        res = super(Canal,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.canal'].search([("codigo","=",False)])
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
         for result in self:
            email = result.env.user.partner_id.email
            if email in ["almacen@dtmindustry.com","rafaguzmang@hotmail.com"]:
                result.disponible = 0
                if result.cantidad - result.apartado > 0:
                    result.disponible = result.cantidad - result.apartado

    def _compute_disponible(self):#-----------------------------Saca la cantidad del material que hay disponible---------------
        for result in self:
            result.disponible = result.cantidad - result.apartado



class NombreMaterial(models.Model):
    _name = "dtm.canal.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Material')

class MaterialEspesor(models.Model):
    _name = "dtm.canal.espesor"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "espesor"

    espesor = fields.Char(string="Espesor")

class MaterialAncho(models.Model):
    _name = "dtm.canal.ancho"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "ancho"

    ancho = fields.Char(string="Ancho", default="0")

class MaterialLargo(models.Model):
    _name = "dtm.canal.largo"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "largo"

    largo = fields.Char(string="Largo", default="0")

class MaterialAlto(models.Model):
    _name = "dtm.canal.alto"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "alto"

    alto = fields.Char(string="Alto", default="0")


   
        
        

            
        


