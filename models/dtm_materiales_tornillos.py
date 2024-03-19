from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re

class Tornillos(models.Model):
    _name = "dtm.materiales.tornillos"
    _description = "Sección para llevar el inventario de los tornillos"
    _rec_name = "material_id"

    material_id = fields.Many2one("dtm.tornillos.nombre",string="Nombre",required=True)
    tipo_id = fields.Many2one("dtm.tornillos.tipo",string="material",required=True)
    diametro_id = fields.Many2one("dtm.tornillos.diametro",string="DIAMETRO", required=True)
    diametro = fields.Float(string="Decimal")
    largo_id = fields.Many2one("dtm.tornillos.largo",string="LARGO", required=True)
    largo = fields.Float(string="Decimal")
    # area = fields.Float(string="Area")
    descripcion = fields.Text(string="Descripción")
    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )

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
        res = super(Tornillos, self).create(vals)
        get_info = self.env['dtm.materiales.tornillos'].search([])
        mapa ={}
        for get in get_info:
            material_id = get.material_id
            tipo_id = get.tipo_id
            diametro_id = get.diametro_id
            diametro = get.diametro
            largo_id = get.largo_id
            largo = get.largo
            cadena = material_id,tipo_id,diametro_id,largo_id,largo,diametro
            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales_tornillos WHERE id="+str(get.id))
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
                    nombre = re.sub("^\s+","",nombre)
                    nombre = re.sub("\s+$","",nombre)
                    medida = get.materials_list.medida
                    medida = re.sub("^\s+","",medida)
                    medida = re.sub("\s+$","",medida)
                    # print("result 1",nombre,medida)

                    if  medida.find(" x ") >= 0 or medida.find(" X "):
                            medida = re.sub("X","x",medida)
                            # print(calibre)
                            if medida.find("x"):
                                diametro = medida[:medida.index("x")-1]
                                largo = medida[medida.index("x")+1:]

                            # Convierte fracciones a decimales
                            regx = re.match("\d+/\d+", diametro)
                            if regx:
                                diametro = float(diametro[0:diametro.index("/")]) / float(diametro[diametro.index("/") + 1:len(diametro)])
                            regx = re.match("\d+/\d+", largo)
                            if regx:
                                largo = float(largo[0:largo.index("/")]) / float(largo[largo.index("/") + 1:len(largo)])
                    # print(nombre,diametro,largo)
                    # Busca coincidencias entre el almacen y el aréa de diseno dtm_diseno_almacen
                    get_mid = self.env['dtm.tornillos.nombre'].search([("nombre","=",nombre)]).id
                    get_angulo = self.env['dtm.materiales.tornillos'].search([("material_id","=",get_mid),("diametro","=",float(diametro)),("largo","=",float(largo))])
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
        res = super(Tornillos,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.tornillos'].search([])
        mapa ={}
        for get in get_info:
            material_id = get.material_id
            tipo_id = get.tipo_id
            diametro_id = get.diametro_id
            diametro = get.diametro
            largo_id = get.largo_id
            largo = get.largo
            cadena = material_id,tipo_id,diametro_id,largo_id,largo,diametro
            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales_tornillos WHERE id="+str(get.id))
                raise ValidationError("Material Duplicado")
            else:
                mapa[cadena] = 1

            cant = self.material_cantidad("dtm.materials.line")
            cant2 = self.material_cantidad("dtm.materials.npi")
            if cant and cant[1] == cant2[1]:
                self.env.cr.execute("UPDATE dtm_materiales SET apartado="+str(cant[0] + cant2[0])+" WHERE id="+str(cant2[1]))

            return res

    @api.onchange("largo_id")
    def _onchange_largo_id(self):
        self.env.cr.execute("UPDATE dtm_tornillos_largo SET  largo='0' WHERE largo is NULL;")
        text = self.largo_id
        text = text.largo
        self.CleanTables("dtm.tornillos.largo","largo")
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
        self.env.cr.execute("UPDATE dtm_tornillos_largo SET  largo='0' WHERE largo    is NULL;")
        text = self.diametro_id
        text = text.diametro
        self.CleanTables("dtm.tornillos.largo","largo")
        if text:
            self.MatchFunction(text)
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                # print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.diametro = result
                # self.area = self.diametro * self.largo

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
            res.append((result.id,f'{result.id}: {result.material_id.nombre} MATERIAL: {result.tipo_id.tipo} DIAMETRO: {result.diametro_id.diametro} LARGO:  {result.largo_id.largo}   '))
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
    _name = "dtm.tornillos.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Material')

class MaterialTipo(models.Model):
    _name = "dtm.tornillos.tipo"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "tipo"

    tipo = fields.Char(string="Tipo")

class MaterialDiametro(models.Model):
    _name = "dtm.tornillos.diametro"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "diametro"

    diametro = fields.Char(string="Diámetro", default="0")

class MaterialLargo(models.Model):
    _name = "dtm.tornillos.largo"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "largo"

    largo = fields.Char(string="Largo", default="0")


