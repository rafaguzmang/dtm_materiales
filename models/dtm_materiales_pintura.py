from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re

class Pintura(models.Model):
    _name = "dtm.materiales.pintura"
    _description = "Sección para llevar el inventario de  pintura"
    _rec_name = "material_id"

    material_id = fields.Many2one("dtm.pintura.nombre",string="MATERIAL",required=True)
    tipo = fields.Selection(string="TIPO", required=True, selection=[('liquida','Líquida'),('polvo','Polvo'),('aerosol','Aerosol')], store = True)
    cantidades = fields.Selection(string="CANTIDADES",  selection=[('litros','Litros'),('kilogramos','Kilogramos'),('piezas','Piezas')],compute="_compute_cantidades", store=True)
    descripcion = fields.Text(string="Descripción")

    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )

    @api.depends("tipo")
    def _compute_cantidades(self):
        for result in self:
            if result.tipo == "liquida":
                result.cantidades = "litros"
            if result.tipo == "polvo":
                result.cantidades = "kilogramos"
            if result.tipo == "aerosol":
                result.cantidades = "piezas"

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
        res = super(Pintura,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.pintura'].search([])
        # print(get_info)
        numero = 1
        for result in get_info:
            # self.env.cr.execute("UPDATE dtm_materiales SET id = "+ str(numero) + " WHERE id = "+ str(result.id))

            if result.cantidad <= 0 and result.apartado == 0:
                self.env.cr.execute("DELETE FROM dtm_materiales_pintura  WHERE id = "+ str(result.id)+";")
            numero += 1
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
            res.append((result.id,f'{result.id}: {result.material_id.nombre} TIPO: {result.tipo} CANTIDADES:  {result.cantidades}'))
        return res

class NombreMaterial(models.Model):
    _name = "dtm.pintura.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Nombre')


