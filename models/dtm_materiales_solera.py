from odoo import api,models,fields
from odoo.exceptions import ValidationError
import re

class Solera(models.Model):
    _name = "dtm.materiales.solera"
    _description = "Sección para llevar el inventario de las solera"
    _rec_name = "material_id"
   
    material_id = fields.Many2one("dtm.solera.nombre",string="MATERIAL",required=True)
    calibre_id = fields.Many2one("dtm.solera.calibre",string="CALIBRE",required=True)
    calibre = fields.Float(string="Decimal")
    largo_id = fields.Many2one("dtm.solera.largo",string="LARGO", required=True)
    largo = fields.Float(string="Decimal")
    ancho_id = fields.Many2one("dtm.solera.ancho",string="ANCHO", required=True)
    ancho = fields.Float(string="Decimal")
    area = fields.Float(string="Area")
    descripcion = fields.Text(string="Descripción")
    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" )

    def write(self,vals):
        res = super(Solera,self).write(vals)
        nombre = "Solera "+  self.material_id.nombre
        medida = str(self.largo) + " x " + str(self.ancho) + " @ " + str(self.calibre)
        get_info = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
        descripcion = ""
        if self.descripcion:
            descripcion = self.descripcion

        if get_info:
            # print("existe")
            print(self.disponible,self.area,descripcion,nombre,medida)
            self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(self.disponible)+", area="+str(self.largo)+", caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' and medida='"+medida+"'")
        else:
            # print("no existe")
            # print(nombre,medida,self.largo,self.disponible)
            get_id = self.env['dtm.diseno.almacen'].search_count([])
            id = get_id + 1
            for result2 in range (1,get_id+1):
                if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                    id = result2
                    break
            self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida, area,caracteristicas) VALUES ("+str(id)+","+str(self.disponible)+", '"+nombre+"', '"+medida+"',"+str(self.largo)+", '"+ descripcion+ "')")

        self.clean_tablas_id("dtm.solera.calibre","calibre")
        self.clean_tablas_id("dtm.solera.largo","largo")
        self.clean_tablas_id("dtm.solera.ancho","ancho")
        return res

    def clean_tablas_id(self,tabla,dato_id): #Borra datos repetidos de las tablas meny2one
        get_campo = self.env[tabla].search([])
        map = {}
        for campo in get_campo:
            if map.get(campo[dato_id]):
                map[campo[dato_id]] = map.get(campo[dato_id])+1
                sust = self.env[tabla].search([(dato_id,"=",campo[dato_id])])[0].id
                dato_id = re.sub("nombre","material",dato_id)
                get_repetido = self.env["dtm.materiales.solera"].search([(dato_id+"_id","=",campo.id)])
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

    @api.model
    def create (self,vals):
        res = super(Solera, self).create(vals)
        get_info = self.env['dtm.materiales.solera'].search([])

        mapa ={}
        for get in get_info:
            material_id = get.material_id
            calibre_id = get.calibre_id
            calibre = get.calibre
            largo_id = get.largo_id
            largo = get.largo
            ancho_id = get.ancho_id
            ancho = get.ancho
            area = get.area
            cadena = material_id,calibre_id,calibre,largo_id,largo,ancho_id,ancho,area

            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales_solera WHERE id="+str(get.id))
                raise ValidationError("Material Duplicado")
            else:
                mapa[cadena] = 1
        return res

#     def material_cantidad(self,modelo):
#         get_mater = self.env['dtm.materials.line'].search([])
#         for get in get_mater:
#             if get:
#                 nombre = str(get.materials_list.nombre)
#                 if  re.match(".*[sS][oO][lL][eE][rR][aA].*",nombre):
#                     nombre = re.sub("^\s+","",nombre)
#                     nombre = nombre[nombre.index(" "):]
#                     nombre = re.sub("^\s+", "", nombre)
#                     nombre = re.sub("\s+$", "", nombre)
#                     medida = get.materials_list.medida
#                     # print("result 1",nombre,medida)
#                     if  medida.find(" x ") >= 0 or medida.find(" X "):
#                         if medida.find(" @ ") >= 0:
#                             # print(nombre)
#                             # nombre = nombre[len("Lámina "):len(nombre)-1]
#                             calibre = medida[medida.index("@")+2:]
#                             medida = re.sub("X","x",medida)
#                             # print(medida)
#                             if medida.find("x"):
#                                 largo = medida[:medida.index("x")-1]
#                                 ancho = medida[medida.index("x")+2:medida.index("@")]
#                             # Convierte fracciones a decimales
#                             regx = re.match("\d+/\d+", calibre)
#                             if regx:
#                                 calibre = float(calibre[0:calibre.index("/")]) / float(calibre[calibre.index("/") + 1:len(calibre)])
#                             regx = re.match("\d+/\d+", largo)
#                             if regx:
#                                 largo = float(largo[0:largo.index("/")]) / float(largo[largo.index("/") + 1:len(largo)])
#                             regx = re.match("\d+/\d+", ancho)
#                             if regx:
#                                 ancho = float(ancho[0:ancho.index("/")]) / float(ancho[ancho.index("/") + 1:len(ancho)])
#                             get_mid = self.env['dtm.solera.nombre'].search([("nombre","=",nombre)]).id
#                             get_solera = self.env['dtm.materiales.solera'].search([("material_id","=",get_mid),("calibre","=",float(calibre)),("largo","=",float(largo)),("ancho","=",float(ancho))])
#                             if get_solera:
#                                 suma = 0
#                                 # print("largo",largo,"ancho",ancho,"calibre", calibre)
#                                 # print(get_solera)
#                                 get_cant = self.env['dtm.materials.line'].search([("nombre","=",get.materials_list.nombre),("medida","=",get.materials_list.medida)])
# #                                 print(get_cant)
#                                 for cant in get_cant:
#                                     suma += cant.materials_cuantity
#                                 return (suma,get_solera.id)



    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Solera,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.solera'].search([])

        mapa = {}
        for get in get_info:
            material_id = get.material_id
            calibre_id = get.calibre_id
            calibre = get.calibre
            largo_id = get.largo_id
            largo = get.largo
            ancho_id = get.ancho_id
            ancho = get.ancho
            area = get.area
            cadena = material_id, calibre_id, calibre, largo_id, largo, ancho_id, ancho, area

            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales_solera WHERE id=" + str(get.id))
            else:
                mapa[cadena] = 1

            nombre = "Solera "+  get.material_id.nombre
            medida = str(get.largo) + " x " + str(get.ancho) + " @ " + str(get.calibre)
            get_esp = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
            if not get.descripcion:
                descripcion = ""
            else:
                descripcion = get.descripcion

            if get_esp:
                self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(get.disponible)+", area="+str(get.largo)+", caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' and medida='"+medida+"'")
            else:
                print(nombre,medida)
                get_id = self.env['dtm.diseno.almacen'].search_count([])
                for result2 in range (1,get_id+1):
                    if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                        id = result2
                        break
                self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida, area,caracteristicas) VALUES ("+str(id)+","+str(get.disponible)+", '"+nombre+"', '"+medida+"',"+str(get.largo)+", '"+ descripcion+ "')")

        return res

    @api.onchange("calibre_id")
    def _onchange_calibre_id(self):
        self.env.cr.execute("UPDATE public.dtm_solera_calibre SET  calibre='0' WHERE calibre is NULL;")
        text = self.calibre_id
        text = text.calibre
        if text:
            self.CleanTables("dtm.solera.calibre","calibre")
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                # print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.calibre = result
                # print(result)


    @api.onchange("largo_id")
    def _onchange_largo_id(self):
        self.env.cr.execute("UPDATE public.dtm_solera_largo SET  largo='0' WHERE largo is NULL;")
        text = self.largo_id
        text = text.largo
        self.CleanTables("dtm.solera.largo","largo")
        if text:
            self.MatchFunction(text)
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                # print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.largo = result
                self.area = self.ancho * self.largo
            if self.ancho > self.largo:

                raise ValidationError("El valor de 'ANCHO' no debe ser mayor que el 'LARGO'")

    @api.onchange("ancho_id")
    def _onchange_ancho_id(self):
        self.env.cr.execute("UPDATE dtm_solera_ancho SET  ancho='0' WHERE ancho    is NULL;")
        text = self.ancho_id
        text = text.ancho
        self.CleanTables("dtm.solera.ancho","ancho")
        if text:
            self.MatchFunction(text)
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                # print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.ancho = result
                self.area = self.ancho * self.largo

            if self.ancho > self.largo:
                raise ValidationError("El valor de 'ANCHO' no debe ser mayor que el 'LARGO'")

    # Filtra si los datos no corresponden al formato de medidas
    def MatchFunction(self,text):
        if text:
            x = re.match('\d\.{0,1}\d*$',text)
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
            res.append((result.id,f'{result.id}: {result.material_id.nombre} CALIBRE: {result.calibre_id.calibre} LARGO:  {result.largo_id.largo}  ANCHO: {result.ancho_id.ancho} '))
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
    _name = "dtm.solera.nombre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Material')

class MaterialCalibre(models.Model):
    _name = "dtm.solera.calibre"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "calibre"

    calibre = fields.Char(string="Calibre")

class MaterialAncho(models.Model):
    _name = "dtm.solera.ancho"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "ancho"

    ancho = fields.Char(string="Ancho", default="0")

class MaterialLargo(models.Model):
    _name = "dtm.solera.largo"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "largo"

    largo = fields.Char(string="Largo", default="0")


   
        
        

            
        


