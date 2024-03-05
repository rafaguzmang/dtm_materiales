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
        res = super(Tubos,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.tubos'].search([])
        # print(get_info)
        numero = 1
        for result in get_info:
            # self.env.cr.execute("UPDATE dtm_materiales SET id = "+ str(numero) + " WHERE id = "+ str(result.id))

            if result.cantidad <= 0 and result.apartado == 0:
                self.env.cr.execute("DELETE FROM dtm_materiales_tubos  WHERE id = "+ str(result.id)+";")
            numero += 1
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

    largo = fields.Char(string="Largo", defaul="0")


