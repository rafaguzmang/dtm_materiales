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





    def consultaAlmacen(self):
         if re.match(".*[Ll][aáAÁ][mM][iI][nN][aA].*",self.descripcion):
            get_alamacen = self.env['dtm.materiales'].search([("codigo","=",self.codigo)])
            pass
         elif re.match(".*[aáAÁ][nN][gG][uU][lL][oO][sS]*.*",self.descripcion):
            pass
         elif re.match(".*[cC][aA][nN][aA][lL].*",self.descripcion):
            pass
         elif re.match(".*[pP][eE][rR][fF][iI][lL].*",self.descripcion):
            pass
         elif re.match(".*[pP][iI][nN][tT][uU][rR][aA].*",self.descripcion):
            pass
         elif re.match(".*[Rr][oO][dD][aA][mM][iI][eE][nN][tT][oO].*",self.descripcion):
            pass
         elif re.match(".*[tT][oO][rR][nN][iI][lL][lL][oO].*",self.descripcion):
            pass
         elif re.match(".*[tT][uU][bB][oO].*",self.descripcion):
            pass
         elif re.match(".*[vV][aA][rR][iI][lL][lL][aA].*",self.descripcion):
            pass


    def convertidor_medidas(self,text):
        text = str(text)

        if re.match(".+\.0$",text):
            print(text[:text.find(".")] +" "+ str(Fraction(text[text.find("."):])))
            return text[:text.find(".")] +" "+ str(Fraction(text[text.find("."):]))

        return text




    def action_done(self):
        if self.material_correcto and self.material_calidad and self.material_aprobado:
            get_compras = self.env['dtm.compras.realizado'].search([("nombre","=",self.descripcion),("proveedor","=",self.proveedor),("codigo","=",self.codigo)])
            # print(get_compras)
            if get_compras:
                cantidad = self.cantidad
                for get in get_compras:
                    # print(get.nombre,get.cantidad)
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
                        # print(cantidad)

                self.consultaAlmacen()
                # Pasa los datos del modulo entradas al de recibido
                get_recibido = self.env['dtm.control.recibido'].search([
                     ("proveedor","=",self.proveedor),
                     ("codigo","=",self.codigo),
                     ("descripcion","=",self.descripcion),
                     ("cantidad","=",self.cantidad),
                     ("fecha_recepcion","=",self.fecha_recepcion),
                     ("fecha_real","=",self.fecha_real),
                     ("material_correcto","=",self.material_correcto),
                     ("material_cantidad","=",self.material_cantidad),
                     ("material_calidad","=",self.material_calidad),
                     ("material_entiempo","=",self.material_entiempo),
                     ("material_aprobado","=",self.material_aprobado),
                     ("motivo","=",self.motivo),
                     ("correctiva","=",self.correctiva),
                     ("cantidad_real","=",self.cantidad_real)
                ])
                 # Pasa los datos del modulo entradas al de entregado
                if not get_recibido:
                    vals = {
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
                        "cantidad_real":self.cantidad_real,
                    }
                #     get_recibido.create(vals)
                # print(self.id)






                # self.env.cr.execute("DELETE FROM dtm_control_entradas WHERE id="+str(self.id))

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

