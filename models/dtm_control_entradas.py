from odoo import api,fields,models
import re
from datetime import datetime
from fractions import Fraction



class Entradas(models.Model):
    _name = "dtm.control.entradas"
    _description = "Modulo para llevar el control de entradas del almacén"

    proveedor = fields.Char(string="Proveedor", readonly=True)
    codigo = fields.Char(string="Codigo", readonly=True)
    descripcion = fields.Char(string="Descripción", readonly=True)
    cantidad = fields.Integer(string="Cantidad", readonly=True)
    fecha_recepcion = fields.Date(string="Fecha estimada de recepción", readonly=True)
    fecha_real = fields.Date(string="Fecha de recepción")
    material_correcto = fields.Boolean(string="Material correcto")
    material_cantidad = fields.Boolean(string="Cantidad correcta")
    material_calidad = fields.Boolean(string="Calidad establecida")
    material_entiempo = fields.Boolean(string="Material a tiempo")
    material_aprobado = fields.Boolean(string="Aprovado")
    motivo = fields.Text(string="Motivo")
    correctiva = fields.Char(string="Acción Correctiva")
    cantidad_real = fields.Integer(string="Recibido")

    def actualizacion(self,material):
         if material:
            cantidad = material.cantidad + self.cantidad_real
            material.write({
                "cantidad": cantidad,
                "disponible":cantidad-material.apartado
            })

    def consultaAlmacen(self):
         if re.match(".*[Ll][aáAÁ][mM][iI][nN][aA].*",self.descripcion):
            get_alamacen = self.env['dtm.materiales'].search([("codigo","=",self.codigo)])
            self.actualizacion(get_alamacen)
         elif re.match(".*[aáAÁ][nN][gG][uU][lL][oO][sS]*.*",self.descripcion):
            get_alamacen = self.env['dtm.materiales.angulos'].search([("codigo","=",self.codigo)])
            self.actualizacion(get_alamacen)
         elif re.match(".*[cC][aA][nN][aA][lL].*",self.descripcion):
            get_alamacen = self.env['dtm.materiales.canal'].search([("codigo","=",self.codigo)])
            self.actualizacion(get_alamacen)
         elif re.match(".*[pP][eE][rR][fF][iI][lL].*",self.descripcion):
            get_alamacen = self.env['dtm.materiales.perfiles'].search([("codigo","=",self.codigo)])
            self.actualizacion(get_alamacen)
         elif re.match(".*[pP][iI][nN][tT][uU][rR][aA].*",self.descripcion):
            get_alamacen = self.env['dtm.materiales.pintura'].search([("codigo","=",self.codigo)])
            self.actualizacion(get_alamacen)
         elif re.match(".*[Rr][oO][dD][aA][mM][iI][eE][nN][tT][oO].*",self.descripcion):
            get_alamacen = self.env['dtm.materiales.rodamientos'].search([("codigo","=",self.codigo)])
            self.actualizacion(get_alamacen)
         elif re.match(".*[tT][oO][rR][nN][iI][lL][lL][oO].*",self.descripcion):
            get_alamacen = self.env['dtm.materiales.tornillos'].search([("codigo","=",self.codigo)])
            self.actualizacion(get_alamacen)
         elif re.match(".*[tT][uU][bB][oO].*",self.descripcion):
            get_alamacen = self.env['dtm.materiales.tubos'].search([("codigo","=",self.codigo)])
            self.actualizacion(get_alamacen)
         elif re.match(".*[vV][aA][rR][iI][lL][lL][aA].*",self.descripcion):
            get_alamacen = self.env['dtm.materiales.varilla'].search([("codigo","=",self.codigo)])
            self.actualizacion(get_alamacen)
         elif re.match(".*[sS][oO][lL][eE][rR][aA].*",self.descripcion):
            get_alamacen = self.env['dtm.materiales.solera'].search([("codigo","=",self.codigo)])
            self.actualizacion(get_alamacen)

    def action_done(self):
        if self.material_correcto and self.material_calidad and self.material_aprobado:
            get_compras = self.env['dtm.compras.realizado'].search([("nombre","=",self.descripcion),("proveedor","=",self.proveedor),("codigo","=",self.codigo)])
            if get_compras:
                cantidad = self.cantidad
                for get in get_compras:
                    if get.cantidad <= cantidad and get.comprado != "comprado":
                        vals = {
                            "comprado": "comprado"
                        }
                        get.write(vals)
                        vals = {
                            "orden_trabajo": get.orden_trabajo,
                            "codigo": get.codigo,
                            "nombre": get.nombre,
                            "cantidad": get.cantidad,
                            "fecha_recepcion": get.fecha_recepcion
                        }
                        self.env['dtm.control.entregado'].create(vals)
                        cantidad -= get.cantidad
                self.consultaAlmacen()
                self.env['dtm.control.recibido'].create({
                     "proveedor":self.proveedor,
                     "codigo":self.codigo,
                     "descripcion":self.descripcion,
                     "cantidad":self.cantidad,
                     "fecha_recepcion":self.fecha_recepcion,
                     "fecha_real":self.fecha_real,
                     "material_correcto":self.material_correcto,
                     "material_cantidad":self.material_cantidad,
                     "material_calidad":self.material_calidad,
                     "material_entiempo":self.material_entiempo,
                     "material_aprobado":self.material_aprobado,
                     "motivo":self.motivo,
                     "correctiva":self.correctiva,
                     "cantidad_real":self.cantidad_real
                })
                record = self.env["dtm.control.entradas"].browse(self.id)
                record.unlink()



                #  # Pasa los datos del modulo entradas al de entregado
                # if not get_recibido:
                #     vals = {
                #         "proveedor":self.proveedor,
                #         "codigo":self.codigo,
                #         "descripcion":self.descripcion,
                #         "cantidad":self.cantidad,
                #         "fecha_recepcion":self.fecha_recepcion,
                #         "fecha_real":self.fecha_real,
                #         "material_correcto":self.material_correcto,
                #         "material_cantidad":self.material_cantidad,
                #         "material_calidad":self.material_calidad,
                #         "material_entiempo":self.material_entiempo,
                #         "material_aprobado":self.material_aprobado,
                #         "motivo":self.motivo,
                #         "correctiva":self.correctiva,
                #         "cantidad_real":self.cantidad_real,
                #     }

    @api.onchange("cantidad_real")
    def _action_cantidad_real(self):
        if self.cantidad_real > self.cantidad:
            self.cantidad_real = self.cantidad

class Recibido(models.Model):
    _name = "dtm.control.recibido"
    _description = "Tabla para llevar registro de los materiales pedidos por el área de compras"
    _order = "id desc"

    proveedor = fields.Char(string="Proveedor", readonly=True)
    codigo = fields.Char(string="Codigo", readonly=True)
    descripcion = fields.Char(string="Descripción", readonly=True)
    cantidad = fields.Integer(string="Cantidad", readonly=True)
    fecha_recepcion = fields.Date(string="Fecha estimada de recepción", readonly=True)
    fecha_real = fields.Date(string="Fecha de recepción", readonly=True)
    material_correcto = fields.Boolean(string="Material correcto", readonly=True)
    material_cantidad = fields.Boolean(string="Cantidad correcta", readonly=True)
    material_calidad = fields.Boolean(string="Calidad establecida", readonly=True)
    material_entiempo = fields.Boolean(string="Material a tiempo", readonly=True)
    material_aprobado = fields.Boolean(string="Aprovado", readonly=True)
    motivo = fields.Text(string="Motivo", readonly=True)
    correctiva = fields.Char(string="Acción Correctiva", readonly=True)
    cantidad_real = fields.Integer(string="Recibido", readonly=True)

class Entregado(models.Model):
    _name = "dtm.control.entregado"
    _description = "Tabla para llevar registro de los materiales entregados a procesos"
    _order = "id desc"

    orden_trabajo = fields.Char(string="Orden de Trabajo")
    codigo = fields.Char(string="Codigo")
    nombre = fields.Char(string="Nombre")
    cantidad = fields.Integer(string="Cantidad")
    fecha_recepcion = fields.Date(string="Fecha de recepción")
    entregado = fields.Char()

    def action_done(self):
        self.entregado = "si"

