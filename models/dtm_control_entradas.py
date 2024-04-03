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

    def action_lamina(self):
        nombre = self.descripcion
        nombre = re.sub("^\s+","",nombre)
        nombre = nombre[nombre.index(" "):nombre.index(" x")]
        nombre = re.sub("[0-9]+[0-9]*.*[0-9]*[0-9]*[0-9]*[0-9]*", "", nombre)
        nombre = re.sub("^\s+","",nombre)
        nombre = re.sub("\s+$","",nombre)
        medida = self.descripcion
        medida = medida[medida.index(nombre)+ len(nombre):]
        medida = re.sub("^\s+","",medida)
        largo = medida[:medida.index("x")]
        largo = re.sub("\s+$","",largo)
        ancho = medida[medida.index("x ")+2:medida.index(" @")]
        calibre = medida[medida.index("@ ")+2:]
        calibre = re.sub("\s+$","",calibre)
        get_nombre = self.env['dtm.nombre.material'].search([("nombre","=",nombre)])
        get_con = self.env['dtm.materiales'].search([("material_id","=",get_nombre.id),("calibre","=",calibre),("ancho","=",ancho),("largo","=",largo)])
        if get_con:
            # print(get_con.cantidad,get_con.apartado)
            cantidad = self.cantidad_real + get_con.cantidad
            apartado = self.cantidad_real + get_con.apartado
            disponible = 0
            if cantidad - apartado > 0:
                disponible = cantidad - apartado
            # print("resultado",cantidad,apartado,disponible)
            vals = {
                "cantidad":cantidad,
                "apartado": apartado,
                "disponible": disponible
            }
            get_con.write(vals)
        else:
            # print("false",get_con)
            if not get_nombre:
                vals = {
                    "nombre":nombre
                }
                get_nombre.create(vals)
                get_nombre = self.env['dtm.nombre.material'].search([("nombre","=",nombre)])

            calibre_val = self.convertidor_medidas(calibre)
            calibre_id = self.env["dtm.calibre.material"].search([("calibre","=",calibre_val)])
            if not calibre_id:
                vals = {
                    "calibre":calibre_val
                }
                calibre_id.create(vals)
                calibre_id = self.env["dtm.calibre.material"].search([("calibre","=",calibre_val)])

            largo_val = self.convertidor_medidas(largo)
            largo_id = self.env["dtm.largo.material"].search([("largo","=",largo_val)])
            if not largo_id:
                vals = {
                    "largo":largo_val
                }
                largo_id.create(vals)
                largo_id = self.env["dtm.largo.material"].search([("largo","=",largo_val)])
            ancho_val = self.convertidor_medidas(ancho)
            ancho_id = self.env["dtm.ancho.material"].search([("ancho","=",ancho_val)])
            if not ancho_id:
                vals = {
                    "ancho":ancho_val
                }
                ancho_id.create(vals)
                ancho_id = self.env["dtm.ancho.material"].search([("ancho","=",ancho_val)])
            vals = {
                "material_id": get_nombre.id,
                "calibre": calibre,
                "ancho": ancho,
                "largo": largo,
                "calibre_id": calibre_id.id,
                "largo_id": largo_id.id,
                "ancho_id": ancho_id.id,
                "cantidad":self.cantidad_real
            }
            # print(get_nombre.id,largo_id.id,ancho_id.id,calibre_id.id)
            get_con.create(vals)

    def action_angulos(self):
        nombre = self.descripcion
        nombre = re.sub("^\s+","",nombre)
        nombre = nombre[nombre.index(" "):nombre.index(" x")]
        nombre = re.sub("[0-9]+[0-9]*.*[0-9]*[0-9]*[0-9]*[0-9]*", "", nombre)
        nombre = re.sub("^\s+","",nombre)
        nombre = re.sub("\s+$","",nombre)
        medida = self.descripcion
        medida = medida[medida.index(nombre)+ len(nombre):]
        medida = re.sub("^\s+","",medida)
        alto = medida[:medida.index("x")]
        alto = re.sub("\s+$","",alto)
        largo = medida[medida.index(",")+1:]
        largo = re.sub("^\s+","",largo)
        largo = re.sub("\s+$","",largo)
        ancho = medida[medida.index("x ")+2:medida.index(" @")]
        calibre = medida[medida.index("@ ")+2:medida.index(",")]
        calibre = re.sub("\s+$","",calibre)
        get_nombre = self.env['dtm.angulos.nombre'].search([("nombre","=",nombre)])
        get_con = self.env['dtm.materiales.angulos'].search([("material_id","=",get_nombre.id),("calibre","=",calibre),("ancho","=",ancho),("largo","=",largo),("alto","=",alto)])
        if get_con:
            cantidad = self.cantidad_real + get_con.cantidad
            apartado = self.cantidad_real + get_con.apartado
            disponible = 0
            if cantidad - apartado > 0:
                disponible = cantidad - apartado
            vals = {
                "cantidad":cantidad,
                "apartado": apartado,
                "disponible": disponible
            }
            get_con.write(vals)
        else:
            if not get_nombre:
                vals = {
                    "nombre":nombre
                }
                get_nombre.create(vals)
                get_nombre = self.env['dtm.angulos.nombre'].search([("nombre","=",nombre)])

            calibre_val = self.convertidor_medidas(calibre)
            calibre_id = self.env["dtm.angulos.calibre"].search([("calibre","=",calibre_val)])
            if not calibre_id:
                vals = {
                    "calibre":calibre_val
                }
                calibre_id.create(vals)
                calibre_id = self.env["dtm.angulos.calibre"].search([("calibre","=",calibre_val)])

            largo_val = self.convertidor_medidas(largo)
            largo_id = self.env["dtm.angulos.largo"].search([("largo","=",largo_val)])
            if not largo_id:
                vals = {
                    "largo":largo_val
                }
                largo_id.create(vals)
                largo_id = self.env["dtm.angulos.largo"].search([("largo","=",largo_val)])
            ancho_val = self.convertidor_medidas(ancho)
            ancho_id = self.env["dtm.angulos.ancho"].search([("ancho","=",ancho_val)])
            if not ancho_id:
                vals = {
                    "ancho":ancho_val
                }
                ancho_id.create(vals)
                ancho_id = self.env["dtm.angulos.ancho"].search([("ancho","=",ancho_val)])
            alto_val = self.convertidor_medidas(alto)
            alto_id = self.env["dtm.angulos.alto"].search([("alto","=",alto_val)])
            if not alto_id:
                vals = {
                    "alto":alto_val
                }
                alto_id.create(vals)
                alto_id = self.env["dtm.angulos.alto"].search([("alto","=",alto_val)])

            vals = { #valores
                "material_id": get_nombre.id,
                "calibre": calibre,
                "ancho": ancho,
                "largo": largo,
                "alto": alto,
                "calibre_id": calibre_id.id,
                "largo_id": largo_id.id,
                "ancho_id": ancho_id.id,
                "alto_id":alto_id.id,
                "cantidad":self.cantidad_real
            }
            get_con.create(vals)

    def action_canales(self):
        nombre = self.descripcion
        nombre = re.sub("^\s+","",nombre)
        nombre = nombre[nombre.index(" "):nombre.index(" x")]
        nombre = re.sub("[0-9]+[0-9]*.*[0-9]*[0-9]*[0-9]*[0-9]*", "", nombre)
        nombre = re.sub("^\s+","",nombre)
        nombre = re.sub("\s+$","",nombre)
        medida = self.descripcion
        medida = medida[medida.index(nombre)+ len(nombre):]
        medida = re.sub("^\s+","",medida)
        largo = medida[medida.index(",")+1:]
        largo = re.sub("^\s+","",largo)
        largo = re.sub("\s+$","",largo)
        ancho = medida[medida.index("x ")+2:medida.index(" espesor")]
        espesor = medida[medida.index("espesor ")+len("espesor")+1:medida.index(",")]
        espesor = re.sub("\s+$","",espesor)
        alto = medida[:medida.index("x")]
        alto = re.sub("\s+$","",alto)
        get_nombre = self.env['dtm.canal.nombre'].search([("nombre","=",nombre)])
        get_con = self.env['dtm.materiales.canal'].search([("material_id","=",get_nombre.id),("espesor","=",espesor),("ancho","=",ancho),("largo","=",largo)])
        if get_con:
            cantidad = self.cantidad_real + get_con.cantidad
            apartado = self.cantidad_real + get_con.apartado
            disponible = 0
            if cantidad - apartado > 0:
                disponible = cantidad - apartado
            vals = {
                "cantidad":cantidad,
                "apartado": apartado,
                "disponible": disponible
            }
            get_con.write(vals)
        else:
            if not get_nombre:
                vals = {
                    "nombre":nombre
                }
                get_nombre.create(vals)
                get_nombre = self.env['dtm.canal.nombre'].search([("nombre","=",nombre)])

            espesor_val = self.convertidor_medidas(espesor)
            espesor_id = self.env["dtm.canal.espesor"].search([("espesor","=",espesor_val)])
            if not espesor_id:
                vals = {
                    "espesor":espesor_val
                }
                espesor_id.create(vals)
                espesor_id = self.env["dtm.canal.espesor"].search([("espesor","=",espesor_val)])

            largo_val = self.convertidor_medidas(largo)
            largo_id = self.env["dtm.canal.largo"].search([("largo","=",largo_val)])
            if not largo_id:
                vals = {
                    "largo":largo_val
                }
                largo_id.create(vals)
                largo_id = self.env["dtm.canal.largo"].search([("largo","=",largo_val)])
            ancho_val = self.convertidor_medidas(ancho)
            ancho_id = self.env["dtm.canal.ancho"].search([("ancho","=",ancho_val)])
            if not ancho_id:
                vals = {
                    "ancho":ancho_val
                }
                ancho_id.create(vals)
                ancho_id = self.env["dtm.canal.ancho"].search([("ancho","=",ancho_val)])
            alto_val = self.convertidor_medidas(alto)
            alto_id = self.env["dtm.canal.alto"].search([("alto","=",alto_val)])
            if not alto_id:
                vals = {
                    "alto":alto_val
                }
                alto_id.create(vals)
                alto_id = self.env["dtm.canal.alto"].search([("alto","=",alto_val)])

            vals = { #valores
                "material_id": get_nombre.id,
                "espesor": espesor,
                "ancho": ancho,
                "largo": largo,
                "alto": alto,
                "espesor_id": espesor_id.id,
                "largo_id": largo_id.id,
                "ancho_id": ancho_id.id,
                "alto_id":alto_id.id,
                "cantidad":self.cantidad_real
            }
            get_con.create(vals)

    def action_perfiles(self):
        nombre = self.descripcion
        nombre = re.sub("^\s+","",nombre)
        nombre = nombre[nombre.index(" "):nombre.index(" x")]
        nombre = re.sub("[0-9]+[0-9]*.*[0-9]*[0-9]*[0-9]*[0-9]*", "", nombre)
        nombre = re.sub("^\s+","",nombre)
        nombre = re.sub("\s+$","",nombre)
        medida = self.descripcion
        medida = medida[medida.index(nombre)+ len(nombre):]
        medida = re.sub("^\s+","",medida)
        alto = medida[:medida.index("x")]
        alto = re.sub("\s+$","",alto)
        largo = medida[medida.index(",")+1:]
        largo = re.sub("^\s+","",largo)
        largo = re.sub("\s+$","",largo)
        ancho = medida[medida.index("x ")+2:medida.index(" @")]
        calibre = medida[medida.index("@ ")+2:medida.index(",")]
        calibre = re.sub("\s+$","",calibre)
        get_nombre = self.env['dtm.perfiles.nombre'].search([("nombre","=",nombre)])
        get_con = self.env['dtm.materiales.perfiles'].search([("material_id","=",get_nombre.id),("calibre","=",calibre),("ancho","=",ancho),("largo","=",largo),("alto","=",alto)])
        if get_con:
            cantidad = self.cantidad_real + get_con.cantidad
            apartado = self.cantidad_real + get_con.apartado
            disponible = 0
            if cantidad - apartado > 0:
                disponible = cantidad - apartado
            vals = {
                "cantidad":cantidad,
                "apartado": apartado,
                "disponible": disponible
            }
            get_con.write(vals)
        else:
            if not get_nombre:
                vals = {
                    "nombre":nombre
                }
                get_nombre.create(vals)
                get_nombre = self.env['dtm.perfiles.nombre'].search([("nombre","=",nombre)])

            calibre_val = self.convertidor_medidas(calibre)
            calibre_id = self.env["dtm.perfiles.calibre"].search([("calibre","=",calibre_val)])
            if not calibre_id:
                vals = {
                    "calibre":calibre_val
                }
                calibre_id.create(vals)
                calibre_id = self.env["dtm.perfiles.calibre"].search([("calibre","=",calibre_val)])

            largo_val = self.convertidor_medidas(largo)
            largo_id = self.env["dtm.perfiles.largo"].search([("largo","=",largo_val)])
            if not largo_id:
                vals = {
                    "largo":largo_val
                }
                largo_id.create(vals)
                largo_id = self.env["dtm.perfiles.largo"].search([("largo","=",largo_val)])
            ancho_val = self.convertidor_medidas(ancho)
            ancho_id = self.env["dtm.perfiles.ancho"].search([("ancho","=",ancho_val)])
            if not ancho_id:
                vals = {
                    "ancho":ancho_val
                }
                ancho_id.create(vals)
                ancho_id = self.env["dtm.perfiles.ancho"].search([("ancho","=",ancho_val)])
            alto_val = self.convertidor_medidas(alto)
            alto_id = self.env["dtm.perfiles.alto"].search([("alto","=",alto_val)])
            if not alto_id:
                vals = {
                    "alto":alto_val
                }
                alto_id.create(vals)
                alto_id = self.env["dtm.perfiles.alto"].search([("alto","=",alto_val)])

            vals = { #valores
                "material_id": get_nombre.id,
                "calibre": calibre,
                "ancho": ancho,
                "largo": largo,
                "alto": alto,
                "calibre_id": calibre_id.id,
                "largo_id": largo_id.id,
                "ancho_id": ancho_id.id,
                "alto_id":alto_id.id,
                "cantidad":self.cantidad_real
            }
            # print(get_nombre.id,calibre_id.id,largo_id.id,ancho_id.id,alto_id.id)
            get_con.create(vals)

    def action_pintura(self):
        nombre = self.descripcion
        nombre = re.sub("^\s+","",nombre)
        nombre = nombre[nombre.index("Pintura")+len("Pintura"):]
        nombre = re.sub("kilogramos", "", nombre)
        nombre = re.sub("litros", "", nombre)
        nombre = re.sub("piezas", "", nombre)
        nombre = re.sub("^\s+","",nombre)
        nombre = re.sub("\s+$","",nombre)
        # print(nombre)
        tipo = self.descripcion
        tipo = re.sub(".*kilogramos.*","polvo",tipo)
        tipo = re.sub(".*litros.*","liquida",tipo)
        tipo = re.sub(".*piezas.*","aerosol",tipo)
        cantidad = tipo
        cantidad = re.sub("polvo","kilogramos",cantidad)
        cantidad = re.sub("liquida","litros",cantidad)
        cantidad = re.sub("aerosol","piezas",cantidad)
        get_nombre = self.env['dtm.pintura.nombre'].search([("nombre","=",nombre)])
        get_con = self.env['dtm.materiales.pintura'].search([("material_id","=",get_nombre.id),("tipo","=",tipo)])
        if get_con:
            # print(get_con.cantidad,get_con.apartado)
            cantidad = self.cantidad_real + get_con.cantidad
            apartado = self.cantidad_real + get_con.apartado
            disponible = 0
            if cantidad - apartado > 0:
                disponible = cantidad - apartado
            # print("resultado",cantidad,apartado,disponible)
            vals = {
                "cantidad":cantidad,
                "apartado": apartado,
                "disponible": disponible
            }
            get_con.write(vals)
        else:
            # print("false",get_con)
            if not get_nombre:
                vals = {
                    "nombre":nombre
                }
                get_nombre.create(vals)
                get_nombre = self.env['dtm.pintura.nombre'].search([("nombre","=",nombre)])

            vals = {
                "material_id": get_nombre.id,
                "tipo": tipo,
                "cantidades": cantidad,
                "cantidad":self.cantidad_real
            }
            # print("Pintura Result",get_nombre.id,tipo,cantidad)
            get_con.create(vals)

    def action_rodamientos(self):
        nombre = self.descripcion
        nombre = re.sub("^\s+","",nombre)
        nombre = re.sub(".*Rodamientos", "", nombre)
        nombre = re.sub("litros", "", nombre)
        nombre = re.sub("piezas", "", nombre)
        nombre = re.sub("^\s+","",nombre)
        nombre = re.sub("\s+$","",nombre)
        get_nombre = self.env['dtm.rodamientos.nombre'].search([("nombre","=",nombre)])
        get_con = self.env['dtm.materiales.rodamientos'].search([("material_id","=",get_nombre.id)])
        if get_con:
            # print(get_con.cantidad,get_con.apartado)
            cantidad = self.cantidad_real + get_con.cantidad
            apartado = self.cantidad_real + get_con.apartado
            disponible = 0
            if cantidad - apartado > 0:
                disponible = cantidad - apartado
            # print("resultado",cantidad,apartado,disponible)
            vals = {
                "cantidad":cantidad,
                "apartado": apartado,
                "disponible": disponible
            }
            get_con.write(vals)
        else:
            # print("false",get_con)
            if not get_nombre:
                vals = {
                    "nombre":nombre
                }
                get_nombre.create(vals)
                get_nombre = self.env['dtm.rodamientos.nombre'].search([("nombre","=",nombre)])

            vals = {
                "material_id": get_nombre.id,
                "cantidad":self.cantidad_real
            }
            get_con.create(vals)

    def action_tornillos(self):
        nombre = self.descripcion
        nombre = re.sub("^\s+","",nombre)
        nombre = nombre[nombre.index(" "):nombre.index(" x")]
        nombre = re.sub("[0-9]+[0-9]*.*[0-9]*[0-9]*[0-9]*[0-9]*", "", nombre)
        nombre = re.sub("^\s+","",nombre)
        nombre = re.sub("\s+$","",nombre)
        medida = self.descripcion
        medida = medida[medida.index(nombre)+ len(nombre):]
        medida = re.sub("^\s+","",medida)
        diametro = medida[:medida.index("x")]
        diametro = re.sub("\s+$","",diametro)
        largo = medida[medida.index("x")+1:]
        largo = re.sub("^\s+","",largo)
        largo = re.sub("\s+$","",largo)

        get_nombre = self.env['dtm.tornillos.nombre'].search([("nombre","=",nombre)])
        get_con = self.env['dtm.materiales.tornillos'].search([("material_id","=",get_nombre.id),("diametro","=",diametro),("largo","=",largo)])
        if get_con:
            cantidad = self.cantidad_real + get_con.cantidad
            apartado = self.cantidad_real + get_con.apartado
            disponible = 0
            if cantidad - apartado > 0:
                disponible = cantidad - apartado
            vals = {
                "cantidad":cantidad,
                "apartado": apartado,
                "disponible": disponible
            }
            get_con.write(vals)
        else:
            if not get_nombre:
                vals = {
                    "nombre":nombre
                }
                get_nombre.create(vals)
                get_nombre = self.env['dtm.tornillos.nombre'].search([("nombre","=",nombre)])

            diametro_val = self.convertidor_medidas(diametro)
            diametro_id = self.env["dtm.tornillos.diametro"].search([("diametro","=",diametro_val)])
            if not diametro_id:
                vals = {
                    "diametro":diametro_val
                }
                diametro_id.create(vals)
                diametro_id = self.env["dtm.tornillos.diametro"].search([("diametro","=",diametro_val)])

            largo_val = self.convertidor_medidas(largo)
            largo_id = self.env["dtm.tornillos.largo"].search([("largo","=",largo_val)])
            if not largo_id:
                vals = {
                    "largo":largo_val
                }
                largo_id.create(vals)
                largo_id = self.env["dtm.tornillos.largo"].search([("largo","=",largo_val)])

            vals = { #valores
                "material_id": get_nombre.id,
                "diametro": diametro,
                "largo": largo,
                "diametro_id": diametro_id.id,
                "largo_id": largo_id.id,
                "cantidad":self.cantidad_real
            }
            print(get_nombre,diametro_id,largo_id)
            print(get_nombre.id,diametro_id.id,largo_id.id)
            get_con.create(vals)

    def action_tubos(self):
        nombre = self.descripcion
        nombre = re.sub("^\s+","",nombre)
        nombre = nombre[nombre.index(" "):nombre.index(" x")]
        nombre = re.sub("[0-9]+[0-9]*.*[0-9]*[0-9]*[0-9]*[0-9]*", "", nombre)
        nombre = re.sub("\.*","",nombre)
        nombre = re.sub("^\s+","",nombre)
        nombre = re.sub("\s+$","",nombre)
        medida = self.descripcion
        medida = medida[medida.index(nombre)+ len(nombre):]
        medida = re.sub("^\s+","",medida)
        diametro = medida[:medida.index("x")]
        diametro = re.sub("\s+$","",diametro)
        largo = medida[medida.index("x ")+2:medida.index(" @")]
        calibre = medida[medida.index("@ ")+2:]
        calibre = re.sub("\s+$","",calibre)
        get_nombre = self.env['dtm.tubos.nombre'].search([("nombre","=",nombre)])
        get_con = self.env['dtm.materiales.tubos'].search([("material_id","=",get_nombre.id),("calibre","=",calibre),("diametro","=",diametro),("largo","=",largo)])
        if get_con:
            cantidad = self.cantidad_real + get_con.cantidad
            apartado = self.cantidad_real + get_con.apartado
            disponible = 0
            if cantidad - apartado > 0:
                disponible = cantidad - apartado
            vals = {
                "cantidad":cantidad,
                "apartado": apartado,
                "disponible": disponible
            }
            get_con.write(vals)
        else:
            if not get_nombre:
                vals = {
                    "nombre":nombre
                }
                get_nombre.create(vals)
                get_nombre = self.env['dtm.tubos.nombre'].search([("nombre","=",nombre)])

            calibre_val = self.convertidor_medidas(calibre)
            calibre_id = self.env["dtm.tubos.calibre"].search([("calibre","=",calibre_val)])
            if not calibre_id:
                vals = {
                    "calibre":calibre_val
                }
                calibre_id.create(vals)
                calibre_id = self.env["dtm.tubos.calibre"].search([("calibre","=",calibre_val)])

            largo_val = self.convertidor_medidas(largo)
            largo_id = self.env["dtm.tubos.largo"].search([("largo","=",largo_val)])
            if not largo_id:
                vals = {
                    "largo":largo_val
                }
                largo_id.create(vals)
                largo_id = self.env["dtm.tubos.largo"].search([("largo","=",largo_val)])
            diametro_val = self.convertidor_medidas(diametro)
            diametro_id = self.env["dtm.tubos.diametro"].search([("diametro","=",diametro_val)])
            if not diametro_id:
                vals = {
                    "diametro":diametro_val
                }
                diametro_id.create(vals)
                diametro_id = self.env["dtm.tubos.diametro"].search([("diametro","=",diametro_val)])


            vals = { #valores
                "material_id": get_nombre.id,
                "calibre": float(calibre),
                "diametro": float(diametro),
                "largo": float(largo),
                "calibre_id": calibre_id.id,
                "largo_id": largo_id.id,
                "diametro_id": diametro_id.id,
                "cantidad":float(self.cantidad_real)
            }

            get_con.create(vals)

    def action_varilla(self):
        nombre = self.descripcion
        nombre = re.sub("^\s+","",nombre)
        nombre = nombre[nombre.index(" "):nombre.index(" x")]
        nombre = re.sub("[0-9]+[0-9]*.*[0-9]*[0-9]*[0-9]*[0-9]*", "", nombre)
        nombre = re.sub("\.*","",nombre)
        nombre = re.sub("^\s+","",nombre)
        nombre = re.sub("\s+$","",nombre)
        medida = self.descripcion
        medida = medida[medida.index(nombre)+ len(nombre):]
        medida = re.sub("^\s+","",medida)
        diametro = medida[:medida.index("x")]
        diametro = re.sub("\s+$","",diametro)
        largo = medida[medida.index("x ")+2:]
        print(medida,diametro)
        get_nombre = self.env['dtm.varilla.nombre'].search([("nombre","=",nombre)])
        get_con = self.env['dtm.materiales.varilla'].search([("material_id","=",get_nombre.id),("diametro","=",diametro),("largo","=",largo)])
        if get_con:
            cantidad = self.cantidad_real + get_con.cantidad
            apartado = self.cantidad_real + get_con.apartado
            disponible = 0
            if cantidad - apartado > 0:
                disponible = cantidad - apartado
            vals = {
                "cantidad":cantidad,
                "apartado": apartado,
                "disponible": disponible
            }
            get_con.write(vals)
        else:
            if not get_nombre:
                vals = {
                    "nombre":nombre
                }
                get_nombre.create(vals)
                get_nombre = self.env['dtm.varilla.nombre'].search([("nombre","=",nombre)])

            largo_val = self.convertidor_medidas(largo)
            largo_id = self.env["dtm.varilla.largo"].search([("largo","=",largo_val)])
            if not largo_id:
                vals = {
                    "largo":largo_val
                }
                largo_id.create(vals)
                largo_id = self.env["dtm.varilla.largo"].search([("largo","=",largo_val)])
            diametro_val = self.convertidor_medidas(diametro)
            diametro_id = self.env["dtm.varilla.diametro"].search([("diametro","=",diametro_val)])
            if not diametro_id:
                vals = {
                    "diametro":diametro_val
                }
                diametro_id.create(vals)
                diametro_id = self.env["dtm.varilla.diametro"].search([("diametro","=",diametro_val)])


            vals = { #valores
                "material_id": get_nombre.id,
                "diametro": float(diametro),
                "largo": float(largo),
                "largo_id": largo_id.id,
                "diametro_id": diametro_id.id,
                "cantidad":float(self.cantidad_real)
            }

            get_con.create(vals)

    def consultaAlmacen(self):
         if re.match(".*[Ll][aáAÁ][mM][iI][nN][aA].*",self.descripcion):
            self.action_lamina()
         elif re.match(".*[aáAÁ][nN][gG][uU][lL][oO][sS]*.*",self.descripcion):
            self.action_angulos()
         elif re.match(".*[cC][aA][nN][aA][lL].*",self.descripcion):
            self.action_canales()
         elif re.match(".*[pP][eE][rR][fF][iI][lL].*",self.descripcion):
            self.action_perfiles()
         elif re.match(".*[pP][iI][nN][tT][uU][rR][aA].*",self.descripcion):
            self.action_pintura()
         elif re.match(".*[Rr][oO][dD][aA][mM][iI][eE][nN][tT][oO].*",self.descripcion):
            self.action_rodamientos()
         elif re.match(".*[tT][oO][rR][nN][iI][lL][lL][oO].*",self.descripcion):
            self.action_tornillos()
         elif re.match(".*[tT][uU][bB][oO].*",self.descripcion):
            self.action_tubos()
         elif re.match(".*[vV][aA][rR][iI][lL][lL][aA].*",self.descripcion):
            print("consulta almacén")
            self.action_varilla()


    def convertidor_medidas(self,text):
        text = str(text)

        if re.match(".+\.0$",text):
            print(text[:text.find(".")] +" "+ str(Fraction(text[text.find("."):])))
            return text[:text.find(".")] +" "+ str(Fraction(text[text.find("."):]))

        return text



        # else:
        #     materiales = self.otros(nombre)

        # if materiales.exists:
        #     get_almacen = self.env['dtm.diseno.almacen'].search([("nombre","=",self.nombre),("medida","=",self.medida)])
        #     print(get_almacen)

    def action_done(self):
        print("Funciona",self.cantidad_real)
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
                        print("Pasa")
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
                    get_recibido.create(vals)





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

