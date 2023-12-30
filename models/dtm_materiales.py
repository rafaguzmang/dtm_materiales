from odoo import api,models,fields
from odoo.exceptions import ValidationError
import re

class Materiales(models.Model):
    _name = "dtm.materiales"
    _rec_name = "material_id"

   
    material_id = fields.Many2one("dtm.nombre.material",string="MATERIAL")
    calibre_id = fields.Many2one("dtm.calibre.material",string="CALIBRE")
    largo_id = fields.Many2one("dtm.largo.material",string="LARGO", default="0")
    ancho_id = fields.Many2one("dtm.ancho.material",string="ANCHO", default="0")
    descripcion = fields.Text(string="Descripción")
    entradas = fields.Integer(string="Entradas")
    cantidad = fields.Integer(string="Stock")
    apartado = fields.Integer(string="Apartado", readonly="True")
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )




    @api.onchange("calibre_id")
    def _onchange_calibre_id(self):
        text = self.calibre_id
        text = text.calibre
        self.CleanTables("dtm.calibre.material","calibre")
        self.MatchFunction(text)

    @api.onchange("largo_id")
    def _onchange_largo_id(self):
        text = self.largo_id
        text = text.largo
        self.CleanTables("dtm.largo.material","largo")
        self.MatchFunction(text)

    @api.onchange("ancho_id")
    def _onchange_ancho_id(self):
        text = self.ancho_id
        text = text.ancho
        self.CleanTables("dtm.ancho.material","ancho")
        self.MatchFunction(text)


    # Filtra si los datos no corresponden al formato de medidas
    def MatchFunction(self,text):
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

    # Limpia los valores de las tablas que no cumplan con el formato de medidas
    def CleanTables(self,table,data):
        get_info = self.env[table].search([])
        table = table.replace(".","_")
        print(get_info)
        for result in get_info:
            print(result[data])

            text = result[data]

            x = re.match('^[\d]+$',text)
            if not x:
                x = re.match("^[\d]+\/[\d]+$",text)
                if not x:
                    x = re.match("^[\d]+ [\d]+\/[\d]+$",text)
                    if not x:
                        self.env.cr.execute("DELETE FROM "+table+" WHERE "+ data +" = '"+ text +"'")



    @api.onchange("entradas")#---------------------------Suma material nuevo------------------------------------------
    def _anchange_cantidad(self):
        # print(self.cantidad)
        self.cantidad += self.entradas

    def accion_salidas(self):#-----------------Resta una unidad al stock----------------------------------------------
        # print(self.cantidad)
        self.cantidad -= 1

    def _compute_disponible(self):#-----------------------------Saca la cantidad del material que hay disponible---------------
        for result in self:
            result.disponible = result.cantidad - result.apartado

    def name_get(self):#--------------------------------Arreglo para cuando usa este modulo como Many2one--------------------
        res = []
        for result in self:
            res.append((result.id,f'{result.material_id.nombre} CALIBRE: {result.calibre_id.calibre} LARGO:  {result.largo_id.largo}  ANCHO: {result.ancho_id.ancho}  CANTIDAD: {result.cantidad} APARTADO: {result.apartado} DISPONIBLE: {result.disponible}'))
        return res




   
        
        

            
        


