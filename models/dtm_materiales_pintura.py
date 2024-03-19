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

    @api.model
    def create (self,vals):
        res = super(Pintura, self).create(vals)
        get_info = self.env['dtm.materiales.pintura'].search([])

        mapa ={}
        for get in get_info:
            material_id = get.material_id
            tipo = get.tipo

            cadena = material_id,tipo

            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales_pintura WHERE id="+str(get.id))
                raise ValidationError("Material Duplicado")
            else:
                mapa[cadena] = 1
        return res
    def material_cantidad(self,modelo):
        get_mater = self.env['dtm.materials.line'].search([])
        for get in get_mater:
             if get:
                nombre = str(get.materials_list.nombre)
                if re.match(".*[pP][iI][nN][tT][uU][rR][aA].*",nombre):
                    nombre = re.sub("^\s+","",nombre)
                    nombre = nombre[nombre.index(" "):]
                    nombre = re.sub("^\s+","",nombre)
                    nombre = re.sub("\s+$","",nombre)
                    medida = get.materials_list.medida
                    medida = re.sub("^\s+","",medida)
                    medida = re.sub("\s+$","",medida)
                    # print("result 1",nombre,medida)
                    # Busca coincidencias entre el almacen y el aréa de diseno dtm_diseno_almacen
                    get_mid = self.env['dtm.pintura.nombre'].search([("nombre","=",nombre)]).id
                    get_angulo = self.env['dtm.materiales.pintura'].search([("material_id","=",get_mid),("cantidades","=",medida)])
                    # print(get_mid,nombre,medida,get_angulo)
                    if get_angulo:
                        suma = 0
                        # print(get.materials_list.nombre,get.materials_list.medida)
                        get_cant = self.env['dtm.materials.line'].search([("nombre","=",get.materials_list.nombre),("medida","=",get.materials_list.medida)])
                        # print(get_cant)
                        for cant in get_cant:
                            suma += cant.materials_cuantity
                        return (suma,get_angulo.id)



    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Pintura,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.pintura'].search([])

        mapa ={}
        for get in get_info:
            material_id = get.material_id
            tipo = get.tipo

            cadena = material_id,tipo

            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales_pintura WHERE id="+str(get.id))
                raise ValidationError("Material Duplicado")
            else:
                mapa[cadena] = 1

            cant = self.material_cantidad("dtm.materials.line")
            cant2 = self.material_cantidad("dtm.materials.npi")
            if cant and cant[1] == cant2[1]:
                self.env.cr.execute("UPDATE dtm_materiales SET apartado="+str(cant[0] + cant2[0])+" WHERE id="+str(cant2[1]))

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


