from odoo import api,models,fields
from odoo.exceptions import ValidationError
import re

class Solera(models.Model):
    _name = "dtm.materiales.canal"
    _description = "Sección para llevar el inventario de las canal"
    _rec_name = "material_id"
   
    material_id = fields.Many2one("dtm.canal.nombre",string="MATERIAL",required=True)
    espesor_id = fields.Many2one("dtm.canal.espesor",string="ESPESOR",required=True)
    espesor = fields.Float(string="Decimal")
    ancho_id = fields.Many2one("dtm.canal.ancho",string="ANCHO", required=True)
    ancho = fields.Float(string="Decimal")
    alto_id = fields.Many2one("dtm.canal.alto",string="ALTO", required=True)
    alto = fields.Float(string="Decimal")
    largo_id = fields.Many2one("dtm.canal.largo",string="LARGO", required=True)
    largo = fields.Float(string="Decimal")
    area = fields.Float(string="Area")
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
        res = super(Solera,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.canal'].search([])
        # print(get_info)
        numero = 1
        for result in get_info:
            # self.env.cr.execute("UPDATE dtm_materiales SET id = "+ str(numero) + " WHERE id = "+ str(result.id))

            if result.cantidad <= 0 and result.apartado == 0:
                self.env.cr.execute("DELETE FROM dtm_materiales_canal  WHERE id = "+ str(result.id)+";")
            numero += 1
        return res

    @api.onchange("espesor_id")
    def _onchange_espesor_id(self):
        self.env.cr.execute("UPDATE public.dtm_canal_espesor SET  espesor='0' WHERE espesor is NULL;")
        text = self.espesor_id
        text = text.espesor
        if text:
            self.CleanTables("dtm.canal.espesor","espesor")
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                # print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.espesor = result
                # print(result)


    @api.onchange("largo_id")
    def _onchange_largo_id(self):
        self.env.cr.execute("UPDATE public.dtm_canal_largo SET  largo='0' WHERE largo is NULL;")
        text = self.largo_id
        text = text.largo
        self.CleanTables("dtm.canal.largo","largo")
        if text:
            self.MatchFunction(text)
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                # print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.largo = result
                self.area = self.ancho * self.largo
            # if self.ancho > self.largo:
            #
            #     raise ValidationError("El valor de 'ANCHO' no debe ser mayor que el 'LARGO'")

    @api.onchange("ancho_id")
    def _onchange_ancho_id(self):
        self.env.cr.execute("UPDATE dtm_canal_ancho SET  ancho='0' WHERE ancho    is NULL;")
        text = self.ancho_id
        text = text.ancho
        self.CleanTables("dtm.canal.ancho","ancho")
        if text:
            self.MatchFunction(text)
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                # print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.ancho = result
                self.area = self.ancho * self.largo

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
            res.append((result.id,f'{result.id}: {result.material_id.nombre} ESPESOR: {result.espesor_id.espesor} LARGO:  {result.largo_id.largo}  ANCHO: {result.ancho_id.ancho} ALTO: {result.alto_id.alto} '))
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
    _name = "dtm.canal.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Material')

class MaterialEspesor(models.Model):
    _name = "dtm.canal.espesor"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "espesor"

    espesor = fields.Char(string="Espesor")

class MaterialAncho(models.Model):
    _name = "dtm.canal.ancho"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "ancho"

    ancho = fields.Char(string="Ancho", default="0")

class MaterialLargo(models.Model):
    _name = "dtm.canal.largo"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "largo"

    largo = fields.Char(string="Largo", defaul="0")

class MaterialAlto(models.Model):
    _name = "dtm.canal.alto"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "alto"

    alto = fields.Char(string="Alto", defaul="0")


   
        
        

            
        


