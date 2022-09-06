
from odoo import models,fields, api
from odoo.exceptions import UserError

class analisistramite(models.Model):
    _name='tram.ana.extincion'
    _rec_name='RefidSolicitud'


    RefidSolicitud = fields.Many2one(comodel_name='tram.sol.extincion', string='Folio de la Solicitud')
    observaciones = fields.Text(string='Observaciones de Analsis')
    attachment = fields.Many2many('ir.attachment', 'ir_attach_anaextincion', 'record_relation_anaextincion', 'attachment_id',
                                  string="Documento de Analisis", tracking=1, required=1)




    def write(self,vals):
        # VALIDACION PARA AGREGAR UN DOCUMENTO
        try:
            existe_doc = vals['attachment']
        except:
            if not self.attachment:
                raise UserError('Es necesario adjuntar la documentación necesaria')
        return super(analisistramite, self).write(vals)