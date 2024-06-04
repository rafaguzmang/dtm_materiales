from odoo import api,models,fields
from odoo.exceptions import ValidationError
import re

class Canal(models.Model):
    _name = "dtm.materiales.canal"
    _description = "Sección para llevar el inventario de las canal"
    _rec_name = "material_id"

    codigo = fields.Integer(string="ID", readonly=True)
    material_id = fields.Many2one("dtm.canal.nombre",string="MATERIAL",required=True)
    espesor_id = fields.Many2one("dtm.canal.espesor",string="ESPESOR",required=True)
    espesor = fields.Float(string="Decimal")
    ancho_id = fields.Many2one("dtm.canal.ancho",string="ANCHO", required=True)
    ancho = fields.Float(string="Decimal")
    alto_id = fields.Many2one("dtm.canal.alto",string="ALTO", required=True)
    alto = fields.Float(string="Decimal", compute="_compute_alto_id", store=True)
    largo_id = fields.Many2one("dtm.canal.largo",string="LARGO", required=True)
    largo = fields.Float(string="Decimal")
    area = fields.Float(string="Area")
    descripcion = fields.Text(string="Descripción")
    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )
    localizacion = fields.Char(string="Localización")

    def accion_guardar(self):
        if not self.descripcion:
            self.descripcion = ""

        get_info = self.env['dtm.materiales.canal'].search([("material_id","=",self.material_id.id),("espesor","=",self.espesor),("largo","=",self.largo),("ancho","=",self.ancho),("alto","=",self.alto)])
        if len(get_info)==1:
             # Agrega los materiales nuevo al modulo de diseño
            nombre = "Canal " + self.material_id.nombre
            medida = str(self.alto) + " x " + str(self.ancho) + " espesor " + str(self.espesor) + ", "+ str(self.largo)
            get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
            if not get_diseno:
                get_id = self.env['dtm.diseno.almacen'].search_count([])

                id = get_id + 1
                for result2 in range (1,get_id):
                    if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                        id = result2
                        break
                self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida, area,caracteristicas) VALUES ("+str(id)+","+str(self.disponible)+", '"+nombre+"', '"+medida+"',"+str(self.largo)+", '"+ self.descripcion + "')")
                get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)], limit = 1)
                self.codigo = get_diseno.id

            else:
                vals = {
                    "cantidad": self.cantidad - self.apartado,
                    "caracteristicas":self.descripcion
                }
                get_diseno.write(vals)
                get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)],limit = 1)
                self.codigo = get_diseno.id

             #Actualiza la lista de materiales de las OT
            get_ot = self.env['dtm.materials.line'].search([("medida","=",get_diseno.medida),("nombre","=",get_diseno.nombre)])
            # print(get_ot)
            self.apartado = 0
            self.disponible = self.cantidad
            for item in get_ot:
                # print(item.materials_cuantity,item.materials_inventory,item.materials_required,self.disponible)
                if self.disponible <= 0:
                    inventory = 0
                    required = item.materials_cuantity
                elif self.disponible - item.materials_cuantity <= 0:
                    inventory = self.disponible
                    required = abs(self.disponible - item.materials_cuantity)
                elif item.materials_cuantity <= self.disponible:
                    inventory = item.materials_cuantity
                    required = 0
                self.apartado +=  item.materials_cuantity
                item.write({
                    "materials_inventory":inventory,
                    "materials_required":required,
                })

                self.disponible = self.cantidad - self.apartado

        elif len(get_info)>1:
            raise ValidationError("Material Duplicado")

    def clean_tablas_id(self,tabla,dato_id): #Borra datos repetidos de las tablas meny2one
        get_campo = self.env[tabla].search([])
        map = {}
        for campo in get_campo:
            if map.get(campo[dato_id]):
                map[campo[dato_id]] = map.get(campo[dato_id])+1
                sust = self.env[tabla].search([(dato_id,"=",campo[dato_id])])[0].id
                dato_id = re.sub("nombre","material",dato_id)
                get_repetido = self.env["dtm.materiales.canal"].search([(dato_id+"_id","=",campo.id)])
                for repetido in get_repetido:
                    vals = {
                        dato_id+"_id": sust
                    }
                    repetido.write(vals)
                tabla_main = re.sub("\.","_",tabla)
                self.env.cr.execute("DELETE FROM "+tabla_main+" WHERE id = "+str(campo.id))

            else:
                map[campo[dato_id]] = 1

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
        res = super(Canal,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.canal'].search([("codigo","=",False)])
        # get_info.unlink()
        return res

    @api.onchange("espesor_id")
    def _onchange_espesor_id(self):
        self.env.cr.execute("UPDATE public.dtm_canal_espesor SET  espesor='0' WHERE espesor is NULL;")
        text = self.espesor_id
        text = text.espesor
        print("on change")
        if text:
            self.CleanTables("dtm.canal.espesor","espesor")
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.espesor = result
                print(result)


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

    @api.depends("alto_id")
    def _compute_alto_id(self):
        self.env.cr.execute("UPDATE dtm_canal_alto SET  alto='0' WHERE alto    is NULL;")
        for result in self:
            text = result.alto_id
            text = text.alto
            result.CleanTables("dtm.canal.alto","alto")
            if text:
                result.MatchFunction(text)
                verdadero = result.MatchFunction(text)
                if verdadero and text:
                    # print(verdadero, text)
                    resultIn = result.convertidor_medidas(text)
                    result.alto = resultIn


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
            x = re.match('\d\.{0,1}\d*$',text)
            if not x:
                x = re.match("^[\d]+\/[\d]+$",text)
                if not x:
                    x = re.match("^[\d]+ [\d]+\/[\d]+$",text)
                    if not x:
                        self.env.cr.execute("DELETE FROM "+table+" WHERE "+ data +" = '"+ str(text) +"'")



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

    largo = fields.Char(string="Largo", default="0")

class MaterialAlto(models.Model):
    _name = "dtm.canal.alto"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "alto"

    alto = fields.Char(string="Alto", default="0")


   
        
        

            
        


