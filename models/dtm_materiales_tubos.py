from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re

class Tubos(models.Model):
    _name = "dtm.materiales.tubos"
    _description = "Sección para llevar el inventario de los tubos"
    _rec_name = "material_id"

    material_id = fields.Many2one("dtm.tubos.nombre",string="MATERIAL",required=True)
    calibre_id = fields.Many2one("dtm.tubos.calibre",string="CALIBRE",required=True)
    calibre = fields.Float(string="Decimal")
    diametro_id = fields.Many2one("dtm.tubos.diametro",string="DIÁMETRO", required=True)
    diametro = fields.Float(string="Decimal", store=True)
    largo_id = fields.Many2one("dtm.tubos.largo",string="LARGO", required=True)
    largo = fields.Float(string="Decimal")
    # area = fields.Float(string="Area")
    descripcion = fields.Text(string="Descripción")
    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )

    def write(self,vals):
        res = super(Tubos,self).write(vals)
        nombre = "Tubo "+  self.material_id.nombre
        medida = str(self.diametro) + " x " + str(self.largo) + " @ " + str(self.calibre)
        get_info = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
        descripcion = ""
        if self.descripcion:
            descripcion = self.descripcion

        if get_info:
            # print("existe")
            # print(self.disponible,self.area,descripcion,nombre,medida)
            print(self.disponible, get_info)
            self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(self.disponible)+", area="+str(self.largo)+", caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' and medida='"+medida+"'")
        else:
            # print("no existe")
            # print(nombre,medida,self.largo,self.disponible)
            get_id = self.env['dtm.diseno.almacen'].search_count([])
            for result2 in range (1,get_id+1):
                if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                    id = result2
                    break
            self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida, area,caracteristicas) VALUES ("+str(id)+","+str(self.disponible)+", '"+nombre+"', '"+medida+"',"+str(self.largo)+", '"+ descripcion+ "')")

        return res

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
        res = super(Tubos, self).create(vals)
        get_info = self.env['dtm.materiales.tubos'].search([])
        mapa ={}
        for get in get_info:
            material_id = get.material_id
            calibre_id = get.calibre_id
            calibre = get.calibre
            diametro_id = get.diametro_id
            diametro = get.diametro
            largo_id = get.largo_id
            largo = get.largo
            cadena = material_id,calibre_id,calibre,largo_id,largo,diametro_id,diametro
            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales_tubos WHERE id="+str(get.id))
                raise ValidationError("Material Duplicado")
            else:
                mapa[cadena] = 1
        return res
    def material_cantidad(self,modelo):
        get_mater = self.env['dtm.materials.line'].search([])
        for get in get_mater:
             if get:
                nombre = str(get.materials_list.nombre)
                if re.match(".*[tT][uU][bB][oO].*",nombre):
                        nombre = re.sub("^\s+","",nombre)
                        nombre = nombre[nombre.index(" "):]
                        nombre = re.sub("^\s+", "", nombre)
                        nombre = re.sub("\s+$", "", nombre)
                        medida = get.materials_list.medida
                        # print("result 1",nombre,medida)
                        if medida.find(" x ") >= 0 or medida.find(" X "):
                            if medida.find("@") >= 0:
                                # print(nombre)
                                # nombre = nombre[len("Lámina "):len(nombre)-1]
                                calibre = medida[medida.index("@")+len("@"):]
                                medida = re.sub("X","x",medida)
                                # print(calibre)
                                if medida.find("x"):
                                    diametro = medida[:medida.index("x")-1]
                                    largo = medida[medida.index("x")+2:medida.index("@")]

                                # Convierte fracciones a decimales
                                regx = re.match("\d+/\d+", calibre)
                                if regx:
                                    calibre = float(calibre[0:calibre.index("/")]) / float(calibre[calibre.index("/") + 1:len(calibre)])
                                regx = re.match("\d+/\d+", largo)
                                if regx:
                                    largo = float(largo[0:largo.index("/")]) / float(largo[largo.index("/") + 1:len(largo)])
                                regx = re.match("\d+/\d+", diametro)
                                if regx:
                                    diametro = float(diametro[0:diametro.index("/")]) / float(diametro[diametro.index("/") + 1:len(diametro)])

                        # print(nombre,diametro,largo)
                        # Busca coincidencias entre el almacen y el aréa de diseno dtm_diseno_almacen
                        get_mid = self.env['dtm.tubos.nombre'].search([("nombre","=",nombre)]).id
                        get_angulo = self.env['dtm.materiales.tubos'].search([("material_id","=",get_mid),("diametro","=",float(diametro)),("largo","=",float(largo)),("calibre","=",float(calibre))])
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
        res = super(Tubos,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.tubos'].search([])
        mapa ={}
        for get in get_info:
            material_id = get.material_id
            calibre_id = get.calibre_id
            calibre = get.calibre
            diametro_id = get.diametro_id
            diametro = get.diametro
            largo_id = get.largo_id
            largo = get.largo
            cadena = material_id,calibre_id,calibre,largo_id,largo,diametro_id,diametro
            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales_tubos WHERE id="+str(get.id))
            else:
                mapa[cadena] = 1

            nombre = "Tubo " + get.material_id.nombre
            medida = str(get.diametro) + " x " + str(get.largo) + " @ " + str(get.calibre)
            get_info = self.env['dtm.diseno.almacen'].search([("nombre", "=", nombre), ("medida", "=", medida)])

            if not get.descripcion:
                descripcion = ""
            else:
                descripcion = get.descripcion

            if get_info:
                self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(get.disponible)+", area="+str(get.largo)+", caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' and medida='"+medida+"'")
            else:
                # print(nombre,medida)
                get_id = self.env['dtm.diseno.almacen'].search_count([])
                for result2 in range (1,get_id+1):
                    if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                        id = result2
                        break
                self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida, area,caracteristicas) VALUES ("+str(id)+","+str(get.disponible)+", '"+nombre+"', '"+medida+"',"+str(get.largo)+", '"+ descripcion+ "')")

            cant = self.material_cantidad("dtm.materials.line")
            cant2 = self.material_cantidad("dtm.materials.npi")
            if cant and cant[1] == cant2[1]:
                self.env.cr.execute("UPDATE dtm_materiales SET apartado="+str(cant[0] + cant2[0])+" WHERE id="+str(cant2[1]))


        return res

    @api.onchange("calibre_id")
    def _onchange_calibre_id(self):
        self.env.cr.execute("UPDATE dtm_tubos_calibre SET  calibre='0' WHERE calibre is NULL;")
        text = self.calibre_id
        text = text.calibre
        if text:
            self.CleanTables("dtm.tubos.calibre","calibre")
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                # print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.calibre = result
                # print(result)

    @api.onchange("largo_id")
    def _onchange_largo_id(self):
        self.env.cr.execute("UPDATE dtm_tubos_largo SET  largo='0' WHERE largo is NULL;")
        text = self.largo_id
        text = text.largo
        self.CleanTables("dtm.tubos.largo","largo")
        if text:
            self.MatchFunction(text)
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                # print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.largo = result
                # self.area = self.ancho * self.largo
            # if self.ancho > self.largo:
                # raise ValidationError("El valor de 'ANCHO' no debe ser mayor que el 'LARGO'")

    @api.onchange("diametro_id")
    def _onchange_diametro_id(self):
        self.env.cr.execute("UPDATE dtm_tubos_diametro SET  diametro='0' WHERE diametro is NULL;")
        text = self.diametro_id
        # print(text)
        text = text.diametro
        self.CleanTables("dtm.tubos.diametro","diametro")
        if text:
            self.MatchFunction(text)
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                # print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.diametro = result

            # if self.ancho > self.largo:
            #     raise ValidationError("El valor de 'ANCHO' no debe ser mayor que el 'LARGO'")

    # Filtra si los datos no corresponden al formato de medidas
    def MatchFunction(self,text):
        if text:
            x = re.match('^[\d]+$',text)
            if not x:
                x = re.match("^[\d]+\/[\d]+$",text)
                if not x:
                    x = re.match("^[\d]+ [\d]+\/[\d]+$",text)
                    if not x:
                        raise ValidationError("Solo se aceptan los siguientes formatos:\n"+
                                              "  1..      \"Números\"\n" +
                                              "  1/1    \"Fracción\"\n" +
                                              "  1 1/1 \"Números espacio fracción\" \n")
                        return False

        return True

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
            res.append((result.id,f'{result.id}: {result.material_id.nombre} CALIBRE: {result.calibre_id.calibre} DIAMETRO: {result.diametro_id.diametro} LARGO:  {result.largo_id.largo}   '))
        return res

    def convertidor_medidas(self,text):
        save = []
        save_float = []
        if re.match("^[\d]+ [\d]+\/[\d]+$",text):
            x = re.split("\s",text)
            for res in x:
              save.append(res)
              if re.match("^[\d]+\/[\d]+$",res):
                x = re.split("\/",res)
                save.remove(res)
                for res in x:
                  save.append(res)
            for res in save:
              save_float.append(float(res))
            sum = save_float[0]+save_float[1]/save_float[2]
            return round(sum,4)
        elif re.match("^[\d]+\/[\d]+$",text):
            x = re.split("\/",text)
            for res in x:
              save.append(float(res))
            sum = save[0]/save[1]
            return round(sum,4)
        else:
            return float(text)

 # Limpia los valores de las tablas que no cumplan con el formato de medidas
    def CleanTables(self,table,data):
        get_info = self.env[table].search([])
        table = table.replace(".","_")
        for result in get_info:
            text = result[data]
            x = re.match('^[\d]+$',text)
            if not x:
                x = re.match("^[\d]+\/[\d]+$",text)
                if not x:
                    x = re.match("^[\d]+ [\d]+\/[\d]+$",text)
                    if not x:
                        self.env.cr.execute("DELETE FROM "+table+" WHERE "+ data +" = '"+ text +"'")



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


