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
    notas = fields.Text()


    def action_done(self):
        if self.material_correcto and self.material_calidad and self.material_aprobado:
            get_compras = self.env['dtm.compras.realizado'].search([("fecha_recepcion","=",self.fecha_recepcion),("nombre","=",self.descripcion),("proveedor","=",self.proveedor),("codigo","=",self.codigo),("cantidad","=",self.cantidad)])
            # Pone el material en comprado del modulo de compras
            if get_compras and get_compras.cantidad <= self.cantidad and get_compras.comprado != "comprado":
                vals = {
                            "comprado": "Recibido",
                            "cantidad_almacen":self.cantidad_real

                        }
                get_compras.write(vals)
                # Se obtienen los datos del inventario y carga el nuevo stock
                get_almacen = self.env['dtm.diseno.almacen'].search([("id","=",self.codigo)])
                # print(get_almacen,get_almacen.cantidad,self.cantidad)
                if get_almacen:
                    get_almacen.write({
                        "cantidad":get_almacen.cantidad + self.cantidad,
                        #Hace la operación necesaria para obtener el disponible
                        "disponible":0 if get_almacen.cantidad + self.cantidad - get_almacen.apartado < 0 else get_almacen.cantidad + self.cantidad - get_almacen.apartado,
                    })
                get_odt = self.env['dtm.odt'].search([],order='id desc')#Se usa para buscar las ordenes que contengan este item y poder hacer los calculos correspondientes
                print(self.codigo,get_odt)
                for odt in get_odt:
                    if int(self.codigo) in odt.materials_ids.materials_list.mapped('id') or int(self.codigo) in odt.maquinados_id.material_id.materials_list.mapped('id'):
                        get_cod = odt.materials_ids.search([("materials_list","=",int(self.codigo))])
                        get_cod_servicios = odt.maquinados_id.material_id.search([("materials_list","=",int(self.codigo))])
                        print("Servicios",get_cod_servicios)
                        for orm in [get_cod, get_cod_servicios]:
                            for item in orm:
                                print("itme",item)
                                get_almacen = self.env['dtm.diseno.almacen'].search([("id","=",self.codigo)])
                                vals = {
                                    "materials_inventory":get_almacen.cantidad,
                                }
                                if get_almacen.disponible >= item.materials_required:
                                    vals["materials_required"] = 0
                                    vals["materials_availabe"] = item.materials_cuantity
                                    get_almacen.write({
                                        "disponible":get_almacen.disponible - item.materials_required
                                })
                                item.write(vals)

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
                self.env["dtm.control.entradas"].search([("id","=",self._origin.id)]).unlink()





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

