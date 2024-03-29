from odoo import api,models,fields
from odoo.exceptions import ValidationError
import re

class Materiales(models.Model):
    _name = "dtm.materiales"
    _description = "Sección para llevar el inventario de las làminas"
    _rec_name = "material_id"
    _description = "Lista de materiales"
   
    material_id = fields.Many2one("dtm.nombre.material",string="MATERIAL",required=True)
    calibre_id = fields.Many2one("dtm.calibre.material",string="CALIBRE",required=True)
    calibre = fields.Float(string="Decimal")
    largo_id = fields.Many2one("dtm.largo.material",string="LARGO", required=True)
    largo = fields.Float(string="Decimal")
    ancho_id = fields.Many2one("dtm.ancho.material",string="ANCHO", required=True)
    ancho = fields.Float(string="Decimal")
    area = fields.Float(string="Area")
    descripcion = fields.Text(string="Descripción")
    entradas = fields.Integer(string="Entradas", default=0)
    cantidad = fields.Integer(string="Stock", default=0)
    apartado = fields.Integer(string="Apartado", readonly="True", default=0)
    disponible = fields.Integer(string="Disponible", readonly="True", compute="_compute_disponible" ,store=True)

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
        res = super(Materiales, self).create(vals)
        get_info = self.env['dtm.materiales'].search([])

        mapa ={}
        for get in get_info:
            material_id = get.material_id
            calibre_id = get.calibre_id
            calibre = get.calibre
            largo_id = get.largo_id
            largo = get.largo
            ancho_id = get.ancho_id
            ancho = get.ancho
            cadena = material_id,calibre_id,calibre,largo_id,largo,ancho_id,ancho

            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales WHERE id="+str(get.id))
                raise ValidationError("Material Duplicado")
            else:
                mapa[cadena] = 1
        return res

    def write(self,vals):
        res = super(Materiales,self).write(vals)
        # print(self.id,self.material_id.nombre,self.calibre,self.largo,self.ancho,self.cantidad,self.disponible)
        nombre = "Lámina " + self.material_id.nombre + " "
        medida = str(self.largo) + " x " + str(self.ancho) + " @ " + str(self.calibre)
        # print(nombre)
        get_info = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])
        # print(get_info)
        descripcion = ""
        if self.descripcion:
            descripcion = self.descripcion
        if get_info:
            # print("existe")
            self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(self.disponible)+", area="+str(self.area)+", caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' and medida='"+medida+"'")
        else:
            # print("no existe")
            get_id = self.env['dtm.diseno.almacen'].search_count([])
            for result2 in range (1,get_id+1):
                if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                    id = result2
                    break
            self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida, area,caracteristicas) VALUES ("+str(id)+","+str(self.disponible)+", '"+nombre+"', '"+medida+"',"+str(self.area)+", '"+ descripcion+ "')")


        return res

#     def material_cantidad(self,modelo):
#          # actualiza el campo de apartado
#         get_mater = self.env[modelo].search([])
#         for get in get_mater:
#             if get:
#                 nombre = str(get.materials_list.nombre)
#                 if  re.match(".*[Ll][aáAÁ][mM][iI][nN][aA][sS]*.*",nombre):
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
#                             get_mid = self.env['dtm.nombre.material'].search([("nombre","=",nombre)]).id
#                             get_lamina = self.env['dtm.materiales'].search([("material_id","=",get_mid),("calibre","=",float(calibre)),("largo","=",float(largo)),("ancho","=",float(ancho))])
#                             if get_lamina:
#                                 suma = 0
#                                 # print("largo",largo,"ancho",ancho,"calibre", calibre)
#                                 # print(get_lamina)
#                                 get_cant = self.env[modelo].search([("nombre","=",get.materials_list.nombre),("medida","=",get.materials_list.medida)])
# #                                 print(get_cant)
#                                 for cant in get_cant:
#                                     suma += cant.materials_cuantity
#                                 return (suma,get_lamina.id)


    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Materiales,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.materiales'].search([])
        mapa = {}
        for get in get_info:
            material_id = get.material_id
            calibre_id = get.calibre_id
            calibre = get.calibre
            largo_id = get.largo_id
            largo = get.largo
            ancho_id = get.ancho_id
            ancho = get.ancho
            cadena = material_id,calibre_id,calibre,largo_id,largo,ancho_id,ancho

            if mapa.get(cadena):
                self.env.cr.execute("DELETE FROM dtm_materiales WHERE id="+str(get.id))
            else:
                mapa[cadena] = 1
                # Agrega los materiales nuevo al modulo de diseño
                nombre = "Lámina " + get.material_id.nombre + " "
                medida = str(get.largo) + " x " + str(get.ancho) + " @ " + str(get.calibre)
                # print(nombre)
                get_info = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])


                if not get.descripcion:
                    descripcion = ""
                else:
                    descripcion = get.descripcion

                # print(get_info.nombre,get_info.medida)
                if get_info:
                    # print("existe")
                    self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(get.disponible)+", area="+str(get.area)+", caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' and medida='"+medida+"'")
                else:
                    # print("no existe")
                    get_id = self.env['dtm.diseno.almacen'].search_count([])
                    for result2 in range (1,get_id+1):
                        if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                            id = result2
                            break
                    self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida, area,caracteristicas) VALUES ("+str(id)+","+str(get.disponible)+", '"+nombre+"', '"+medida+"',"+str(get.area)+", '"+ descripcion+ "')")



        return res

    @api.onchange("calibre_id")
    def _onchange_calibre_id(self):
        self.env.cr.execute("UPDATE public.dtm_calibre_material SET  calibre='0' WHERE calibre is NULL;")
        text = self.calibre_id
        text = text.calibre
        if text:
            self.CleanTables("dtm.calibre.material","calibre")
            verdadero = self.MatchFunction(text)
            if verdadero and text:
                # print(verdadero, text)
                result = self.convertidor_medidas(text)
                self.calibre = result
                # print(result)


    @api.onchange("largo_id")
    def _onchange_largo_id(self):
        self.env.cr.execute("UPDATE public.dtm_largo_material SET  largo='0' WHERE largo is NULL;")
        text = self.largo_id
        text = text.largo
        self.CleanTables("dtm.largo.material","largo")
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
        self.env.cr.execute("UPDATE public.dtm_ancho_material SET  ancho='0' WHERE ancho is NULL;")

        text = self.ancho_id
        text = text.ancho
        self.CleanTables("dtm.ancho.material","ancho")
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

    # def _compute_disponible(self):#-----------------------------Saca la cantidad del material que hay disponible---------------
    #     for result in self:
    #         result.disponible = result.cantidad - result.apartado

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
    _name = "dtm.nombre.material"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "nombre"

    nombre = fields.Char(string= 'Material')

class MaterialCalibre(models.Model):
    _name = "dtm.calibre.material"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "calibre"

    calibre = fields.Char(string="Calibre")

class MaterialAncho(models.Model):
    _name = "dtm.ancho.material"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "ancho"

    ancho = fields.Char(string="Ancho", default="0")

class MaterialLargo(models.Model):
    _name = "dtm.largo.material"
    _description = "Se guardan los diferentes tipos de valores"
    _rec_name = "largo"

    largo = fields.Char(string="Largo", default="0")


   
        
        

            
        


