
from odoo import models,fields, api
from odoo.exceptions import UserError
from datetime import date

class oficioRequerimiento(models.Model):
    _name='tram.req.extincion'
    _rec_name ='RefidSolicitud'


    RefidSolicitud = fields.Many2one(comodel_name='tram.sol.extincion', string='Folio de la Solicitud')
    observaciones = fields.Text(string='Observaciones de Requerimiento')
    fechadocumento = fields.Date(string='Fecha del Oficio', required=1)
    estatus = fields.Selection([('pendiente', 'Pendiente de Notificar'),
                                    ('notificado', 'Notificado')],
                                   default="pendiente",
                                   string='Oficio de requerimiento' ,group_expand='_expand_states')

    oficiorequerimiento = fields.Many2many('ir.attachment', 'ir_attach_reqextincion', 'record_relation_extincion_req', 'attachment_id',
                                  string="Oficio de Requerimiento", tracking=1, required=1)
    exp = fields.Char(string="Expediente")
    no_officio = fields.Char(string="No. Oficio:")
    attention = fields.Date(string="Y en atención a su escrito recibido con fecha")
    submit = fields.Text(string="Remitan lo siguiente:")
    leyenda_requerimiento = fields.Char(compute="_get_leyendas")

    def reporte_oficio_requerimiento(self):
        return self.env.ref('extincion.formato_oficio_requerimiento').report_action(self)

    def get_elaboro(self):
        tramite = self.env['tramite.gestion.extincion'].sudo().search([('RefidSolicitud', '=', self.RefidSolicitud.id)])
        return tramite.RefIdUsuario.name

    def get_elaboro_email(self):
        tramite = self.env['tramite.gestion.extincion'].sudo().search([('RefidSolicitud', '=', self.RefidSolicitud.id)])
        return tramite.RefIdUsuario.login

    def _get_year(self):
        return date.today().year
    year = fields.Char(string="Año en curso", default=_get_year)

    def notificariap(self):
        refidsolicitud = self.RefidSolicitud.id
        usuario_create = self.RefidSolicitud.create_uid
        for record in self:
            if not record.oficiorequerimiento:
                raise UserError('Es necesario adjuntar la documentación necesaria')

            filtros = [('id', '=', refidsolicitud),('status','=','enviado')]
            folio_obj = self.env['tram.sol.extincion'].sudo().search(filtros)

            #SE ACTUALIZA EL ESTATUS A ENVIADO EL FOLIO DE LA IAP
            folio_obj.write({'status':'notificado'})

            usuario = self.env['res.users'].sudo().search([('id', '=', usuario_create.id)])

            # SE OBTIENE EL USUARIO QUE CREO LA SOLICITUD PARA OBTENER SU IAP
            for company in usuario.company_ids:
                iap = company.partner_id

                # SE ACTUALIZA EL ESTATOS DE LA TABLA DE TRAMITE GESTION  PARA QUE SE VEA EN EL BUZON
                filtros = [('RefIdIAP', '=', iap.id), ('RefIdTipoTram', '=', 11),
                           ('RefidSolicitud', '=', refidsolicitud)]
                tramite_gestionobj = self.env['tramite.gestion'].sudo().search(filtros)
                if tramite_gestionobj:
                    tramite_gestionobj.write({'EstatusAsunto':'notificado'})

        record.write({'estatus': 'notificado'})


        template = self.env.ref('extincion.solicitud_requerimiento')
        template.send_mail(self.id, force_send=True)

    def write(self, vals):
        filtro_req = [('id','=',self.id),
                      ('RefidSolicitud','=',self.RefidSolicitud.id)]
        solicitudenviado_obj = self.env['tram.req.extincion'].sudo().search(filtro_req)

        if solicitudenviado_obj.estatus == 'notificado':
            raise UserError(('Ya realizó la notificacion a la Institución y no puede modificar su registro'))
        return super(oficioRequerimiento, self).write(vals)

    def _get_leyendas(self):
        for record in self:
            filtros = [('id', '=', self.RefidSolicitud.id), ('status', '=', 'notificado')]
            folio_obj = self.env['tram.sol.extincion'].sudo().search(filtros)
            vnombredir = folio_obj.tipotram.leyendarequerimiento
            record.leyenda_requerimiento = vnombredir