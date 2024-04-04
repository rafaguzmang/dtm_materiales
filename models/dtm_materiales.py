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
            id = get_id + 1
            for result2 in range (1,get_id+1):
                if not self.env['dtm.diseno.almacen'].search([("id","=",result2)]):
                    id = result2
                    break
            self.env.cr.execute("INSERT INTO dtm_diseno_almacen ( id,cantidad, nombre, medida, area,caracteristicas) VALUES ("+str(id)+","+str(self.disponible)+", '"+nombre+"', '"+medida+"',"+str(self.area)+", '"+ descripcion+ "')")

        self.clean_tablas_id("dtm.calibre.material","calibre")
        self.clean_tablas_id("dtm.largo.material","largo")
        self.clean_tablas_id("dtm.ancho.material","ancho")
        # self.clean_tablas_id("dtm.nombre.material","nombre")


        return res

    def clean_tablas_id(self,tabla,dato_id): #Borra datos repetidos de las tablas meny2one
        get_campo = self.env[tabla].search([])
        map = {}
        for campo in get_campo:
            print(campo[dato_id])
            if map.get(campo[dato_id]):
                map[campo[dato_id]] = map.get(campo[dato_id])+1
                print(campo[dato_id],campo.id,dato_id)
                sust = self.env[tabla].search([(dato_id,"=",campo[dato_id])])[0].id
                dato_id = re.sub("nombre","material",dato_id)
                get_repetido = self.env["dtm.materiales"].search([(dato_id+"_id","=",campo.id)])
                for repetido in get_repetido:
                    vals = {
                        dato_id+"_id": sust
                    }
                    repetido.write(vals)
                    print(repetido)
                tabla_main = re.sub("\.","_",tabla)
                print(tabla_main)
                self.env.cr.execute("DELETE FROM "+tabla_main+" WHERE id = "+str(campo.id))

            else:
                map[campo[dato_id]] = 1



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
                get_diseno = self.env['dtm.diseno.almacen'].search([("nombre","=",nombre),("medida","=",medida)])

                if not get.descripcion:
                    descripcion = ""
                else:
                    descripcion = get.descripcion
                # print(get_diseno)
                # print(get_diseno.nombre,get_diseno.medida)
                if get_diseno:
                    # print("existe")
                    self.env.cr.execute("UPDATE dtm_diseno_almacen SET cantidad="+str(get.disponible)+", area="+str(get.area)+", caracteristicas='"+descripcion+"' WHERE nombre='"+nombre+"' and medida='"+medida+"'")
                else:
                    get_id = self.env['dtm.diseno.almacen'].search_count([])
                    # print("no existe",get_id)
                    id = get_id + 1
                    for result2 in range (1,get_id):
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
            x = re.match('\d\.{0,1}\d*$',text)
            if not x:
                x = re.match("^[\d]+\/[\d]+$",text)
                if not x:
                    x = re.match("^[\d]+ [\d]+\/[\d]+$",text)
                    if not x:
                        self.env.cr.execute("DELETE FROM "+table+" WHERE "+ data +" = '"+ text +"'")

        # get_calibre = self.env['dtm.calibre.material'].search([])
        # map = {}
        # for calibre in get_calibre:
        #     # print(calibre.calibre)
        #     if map.get(calibre.calibre):
        #         map[calibre.calibre] = map.get(calibre.calibre)+1
        #         print(calibre.id)
        #         sust = self.env['dtm.calibre.material'].search([("calibre","=",calibre.calibre)])[0].id
        #         get_repetido = self.env["dtm.materiales"].search([("calibre_id","=",calibre.id)])
        #         for repetido in get_repetido:
        #             vals = {
        #                 "calibre_id": sust
        #             }
        #             repetido.write(vals)
        #             print(repetido)
        #
        #     else:
        #         map[calibre.calibre] = 1
        #
        # print(map)




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


   
        
        

            
        


