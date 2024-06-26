from odoo import api,models,fields
from datetime import datetime


class OrdenTrabajo(models.Model):
    _name = "dtm.almacen.odt"
    _inherit = ['mail.thread']
    _description = "Modelo para ver los materiales solicitados por parte de diseño"
    _order = "id desc"

    ot_number = fields.Integer(string="NÚMERO DE ORDEN",readonly=True)
    tipe_order = fields.Char(string="TIPO",readonly=True)
    date_in = fields.Date(string="FECHA DE ENTRADA", default= datetime.today(),readonly=True)
    date_rel = fields.Date(string="FECHA DE ENTREGA", default= datetime.today())
    color = fields.Char(string="COLOR",default="N/A")
    materials_ids = fields.Many2many("dtm.materials.line", readonly=True)
    materials_npi_ids = fields.Many2many("dtm.materials.npi",readonly=True)
    firma = fields.Char(string="Firmato")

    #---------------------Resumen de descripción------------

    description = fields.Text(string="DESCRIPCIÓN")

    #------------------------Notas---------------------------

    notes = fields.Text(string="notes")

    def accion_firma(self):
        self.firma = "Firmado"
        get_ot = self.env['dtm.odt'].search([("ot_number","=",self.ot_number)])
        get_ot.write({"firma_almacen": self.env.user.partner_id.name})
        get_procesos = self.env['dtm.proceso'].search([("ot_number","=",self.ot_number)])
        get_procesos.write({
            "firma_almacen": self.env.user.partner_id.name,
            "firma_almacen_kanba":"Almacén"
        })


