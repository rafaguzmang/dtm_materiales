from odoo import api,fields,models
from odoo.exceptions import ValidationError
import re


class Angulos(models.Model):
    _name = "dtm.materiales.angulos"
    _description = "Sección para llevar el inventario de los angulos"
    _rec_name = "material_id"

    codigo = fields.Integer(string="Código", readonly=True)
    material_id = fields.Many2one("dtm.angulos.nombre",string="MATERIAL",required=True)
    calibre = fields.Float(string="Calibre")
    largo = fields.Float(string="Largo")
    ancho = fields.Float(string="Ancho")
    alto = fields.Float(string="Alto")
    area = fields.Float(string="Area")
    descripcion = fields.Text(string="Descripción")
    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible",store=True )
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

            nombre = f"Ángulos {self.material_id.nombre}"
            medida = f"{self.alto} x {self.ancho} @ {self.calibre}, {self.largo}"
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
        res = super(Angulos,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.angulos'].search([("codigo","=",False)])
        get_info.unlink()

        email = self.env.user.partner_id.email
        self.user_almacen = False
        if email in ["almacen@dtmindustry.com","rafaguzmang@hotmail.com"]:
            self.user_almacen = True
        return res

    @api.onchange("ancho_id")
    def _onchange_ancho_id(self):
        self.env.cr.execute("UPDATE dtm_angulos_ancho SET  ancho='0' WHERE ancho    is NULL;")
        text = self.ancho_id
        text = text.ancho
        self.CleanTables("dtm.angulos.ancho","ancho")
        if text:
            self.MatchFunction(text)
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                result = self.convertidor_medidas(text)
                self.ancho = result

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

    @api.depends("cantidad")
    def _compute_disponible(self):#-----------------------------Saca la cantidad del material que hay disponible---------------
       for result in self:
            result.disponible = result.cantidad - result.apartado


    # def name_get(self):#--------------------------------Arreglo para cuando usa este modulo como Many2one--------------------
    #     res = []
    #     for result in self:
    #         res.append((result.id,f'{result.id}: {result.material_id.nombre} CALIBRE: {result.calibre_id.calibre} ALTO: {result.alto_id.alto} ANCHO: {result.ancho_id.ancho} LARGO:  {result.largo_id.largo}') )
    #     return res

class NombreMaterial(models.Model):
    _name = "dtm.angulos.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Material')

class MaterialCalibre(models.Model):
    _name = "dtm.angulos.calibre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "calibre"

    calibre = fields.Char(string="Calibre")

class MaterialAncho(models.Model):
    _name = "dtm.angulos.ancho"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "ancho"

    ancho = fields.Char(string="Ancho", default="0")

class MaterialLargo(models.Model):
    _name = "dtm.angulos.largo"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "largo"

    largo = fields.Char(string="Largo", default="0")

class MaterialLargo(models.Model):
    _name = "dtm.angulos.alto"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "alto"

    alto = fields.Char(string="Alto", default="0")
