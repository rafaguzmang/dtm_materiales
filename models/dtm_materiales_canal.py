from odoo import api,models,fields
from odoo.exceptions import ValidationError
import re

class Canal(models.Model):
    _name = "dtm.materiales.canal"
    _description = "Sección para llevar el inventario de las canal"
    _rec_name = "material_id"
   
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

    def write(self,vals):
        res = super(Canal,self).write(vals)
        nombre = "Canal "+  self.material_id.nombre
        medida = str(self.alto) + " x " + str(self.ancho) + " espesor " + str(self.espesor) +", " + str(self.largo)
        get_info = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])

        descripcion = ""
        if not self.descripcion:
            descripcion = self.descripcion

        if get_info:
            # print("existe")
            print(self.disponible,self.area,descripcion,nombre,medida)
            self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(self.disponible)+", area="+str(self.largo)+", caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' and medida='"+medida+"'")
        else:
            # print("no existe")
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
        res = super(Canal, self).create(vals)
        get_info = self.env['dtm.materiales.canal'].search([])
        mapa ={}
        for get in get_info:
            material_id = get.material_id
            espesor_id = get.espesor_id
            espesor = get.espesor
            ancho_id = get.ancho_id
            ancho = get.ancho
            alto_id = get.alto_id
            alto = get.alto
            largo_id = get.largo_id
            largo = get.largo
            area = get.area
            cadena = material_id,espesor_id,espesor,largo_id,largo,ancho_id,ancho,area,alto,alto_id
            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales_canal WHERE id="+str(get.id))
                raise ValidationError("Material Duplicado")
            else:
                mapa[cadena] = 1

        return res

    def material_cantidad(self,modelo):
         # actualiza el campo de apartado
            get_mater = self.env['dtm.materials.line'].search([])
            for get in get_mater:
                 if get:
                    nombre = str(get.materials_list.nombre)
                    if re.match(".*[cC][aA][nN][aA][lL].*",nombre):
                        nombre = re.sub("^\s+","",nombre)
                        nombre = nombre[nombre.index(" "):]
                        nombre = re.sub("^\s+", "", nombre)
                        nombre = re.sub("\s+$", "", nombre)
                        medida = get.materials_list.medida
                        # print("result 1",nombre,medida)
                        if  medida.find(" x ") >= 0 or medida.find(" X "):
                            if medida.find(" espesor ") >= 0:
                                # print(nombre)
                                # nombre = nombre[len("Lámina "):len(nombre)-1]
                                calibre = medida[medida.index("espesor")+len("espesor"):medida.index(",")]
                                medida = re.sub("X","x",medida)
                                # print(calibre)
                                if medida.find("x"):
                                    alto = medida[:medida.index("x")-1]
                                    ancho = medida[medida.index("x")+2:medida.index("espesor")]
                                    largo = medida[medida.index(",")+1:]

                                # Convierte fracciones a decimales
                                regx = re.match("\d+/\d+", calibre)
                                if regx:
                                    calibre = float(calibre[0:calibre.index("/")]) / float(calibre[calibre.index("/") + 1:len(calibre)])
                                regx = re.match("\d+/\d+", largo)
                                if regx:
                                    largo = float(largo[0:largo.index("/")]) / float(largo[largo.index("/") + 1:len(largo)])
                                regx = re.match("\d+/\d+", ancho)
                                if regx:
                                    ancho = float(ancho[0:ancho.index("/")]) / float(ancho[ancho.index("/") + 1:len(ancho)])
                                regx = re.match("\d+/\d+", alto)
                                if regx:
                                    alto = float(ancho[0:ancho.index("/")]) / float(ancho[ancho.index("/") + 1:len(ancho)])

                                # Busca coincidencias entre el almacen y el aréa de diseno dtm_diseno_almacen
                                get_mid = self.env['dtm.canal.nombre'].search([("nombre","=",nombre)]).id
                                get_angulo = self.env['dtm.materiales.canal'].search([("material_id","=",get_mid),("espesor","=",float(calibre)),("largo","=",float(largo)),("ancho","=",float(ancho)),("alto","=",float(alto))])
                                # print("largo",largo,"ancho",ancho,"espesor", calibre,"alto",alto,get_angulo)
                                if get_angulo:
                                    suma = 0
                                    # print(get_angulo)
                                    get_cant = self.env['dtm.materials.line'].search([("nombre","=",get.materials_list.nombre),("medida","=",get.materials_list.medida)])
                                    # print(get_cant)
                                    for cant in get_cant:
                                        suma += cant.materials_cuantity
                                        self.env.cr.execute("UPDATE dtm_materiales_canal SET apartado="+str(suma)+" WHERE id="+str(get_angulo.id))


                                    return (suma,get_angulo.id)



    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Canal,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales.canal'].search([])

        mapa ={}
        for get in get_info:
            material_id = get.material_id
            espesor_id = get.espesor_id
            espesor = get.espesor
            ancho_id = get.ancho_id
            ancho = get.ancho
            alto_id = get.alto_id
            alto = get.alto
            largo_id = get.largo_id
            largo = get.largo
            area = get.area
            cadena = material_id,espesor_id,espesor,largo_id,largo,ancho_id,ancho,area,alto,alto_id

            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales_canal WHERE id="+str(get.id))
            else:
                mapa[cadena] = 1

            nombre = "Canal " + get.material_id.nombre
            medida = str(get.alto) + " x " + str(get.ancho) + " espesor " + str(get.espesor) +", " + str(get.largo)
            get_esp = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])

            if not get.descripcion:
                descripcion = ""
            else:
                descripcion = get.descripcion

            # print(get,nombre,medida,get.disponible)

            if get_esp:
                # print("existe")
                self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(get.disponible)+", area="+str(get.alto)+", caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' and medida='"+medida+"'")
            else:
                get_id = self.env['dtm.diseno.almacen'].search_count([])
                for result2 in range (1,get_id+1):
                    if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                        id = result2
                        break
                self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida, area,caracteristicas) VALUES ("+str(id)+","+str(get.disponible)+", '"+nombre+"', '"+medida+"',"+str(get.alto)+", '"+ descripcion+ "')")


            cant = self.material_cantidad("dtm.materials.line")
            cant2 = self.material_cantidad("dtm.materials.npi")
            if cant and cant[1] == cant2[1]:
                self.env.cr.execute("UPDATE dtm_materiales SET apartado="+str(cant[0] + cant2[0])+" WHERE id="+str(cant2[1]))


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

    largo = fields.Char(string="Largo", default="0")

class MaterialAlto(models.Model):
    _name = "dtm.canal.alto"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "alto"

    alto = fields.Char(string="Alto", default="0")


   
        
        

            
        


