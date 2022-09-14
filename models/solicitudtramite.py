import re

from odoo import models,fields, api
from odoo.exceptions import UserError, ValidationError, Warning
import pathlib

class solicitud(models.Model):
    _name='tram.sol.extincion'
    _rec_name = 'id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    status = fields.Selection(
        [('pendiente', 'Pendiente de enviar'), ('enviado', 'Enviado'), ('notificado', 'Notificado'), ('autorizado', 'Autorizado'),
         ('rechazado', 'Rechazado')])

    def get_tramitebase(self):
        return self.env['cf.tipos.tramites'].sudo().search([('id', 'in', [11])])
    tipotram = fields.Many2one(comodel_name='cf.tipos.tramites', string='Tipo de Trámite', default=get_tramitebase)
    callenotif = fields.Char(string="Calle", required=1,tracking=1)
    noexteriornotif =fields.Char(string="No. Exterior", required=1,tracking=1)
    nointeriornotif = fields.Char(string="No. Int")
    cpnotif = fields.Char(string="CP", required=1,tracking=1, size=5)
    colonianotif = fields.Char(string="Colonia", required=1, tracking=1)

    state_id = fields.Many2one(comodel_name='res.country.state', domain="[('country_id', '=', 156)]", string='Estado', default=493,  tracking=1)
        #'res.country.state', 'Estado', domain="[('country_id', '=', 156)]", default=493,  tracking=1)
    city_id = fields.Many2one(
        'res.country.state.city', 'Municipio/Alcaldía', domain="[('state_id', '=', state_id)]", required=1, tracking=1)


    correonotif = fields.Char(string="Correo electrónico", required=1,tracking=1)
    personaautorizadas = fields.Char(string="Nombre(s)", required=1,tracking=1)
    attachment = fields.Many2many('ir.attachment', 'ir_attach_extincion', 'record_relation_extincion', 'attachment_id',
                                  string="Documentacion Anexa contratos de extinción", tracking=1, required=1)

    response_to_request_extincion = fields.Many2many('ir.attachment', 'ir_attach_edofin_extincion', 'record_relation_edofin_extincion', 'attachment_id',
                                  string="Respuesta al requerimiento", tracking=1, required=1)
    response_to_request_extincion_boolean = fields.Boolean(string="Esconder boton",
                                                          compute='_compute_response_to_request_extincion_boolean',
                                                          store=False)

    @api.depends('response_to_request_extincion')
    def _compute_response_to_request_extincion_boolean(self):
        if not self.response_to_request_extincion:
            self.response_to_request_extincion_boolean = True
        else:
            self.response_to_request_extincion_boolean = False

    estatusjap = fields.Text(compute="_get_estatus")
    asesortramite = fields.Text(compute="_get_asesor")
    correosavisos = fields.Text(compute="_get_correos")
    correosavisosjefes = fields.Text(compute="_get_jefes")

    apoderados_id = fields.Many2one(comodel_name='apoderados',
                                     required=1, tracking=1, help="Lista de apoderados autorizados")

    fecha_apoderado = fields.Date(related="apoderados_id.fechaescritura")
    escritura_apoderado = fields.Char(related="apoderados_id.noescritura")

    nombrecompletoapoderado = fields.Char(compute="_get_nombrecompletoapoderado")

    pnombre = fields.Char(related="apoderados_id.primernombre", string="El firmante será")
    snombre = fields.Char(related="apoderados_id.segundonombre")
    apaterno = fields.Char(related="apoderados_id.primerapellido")
    amaterno = fields.Char(related="apoderados_id.segundoapellido")

    tipo_poder = fields.Many2many(related="apoderados_id.refidpoder")

    #Formato de Escrito solicitud
    applicant = fields.Char(string="Solicitante")
    in_my_character = fields.Char(string="En  mi carácter de")
    prove_in_terms = fields.Char(string="Que acredito en términos")
    celebrate_on = fields.Date(string="Celebrada el")
    celebrate_on_day = fields.Date(string="Sesión Extraordinaria  de Patronato, celebrada el día")
    assist_celebrate_on = fields.Date(string="Sesión extraordinaria de Patronos, celebrada el día")
    financial_information = fields.Date(string="Información financiera que reflejan cifras al día")
    write_by_him = fields.Char(string="Escrito por el que el")
    located_in = fields.Char(string="El ubicado en")
    authorizing = fields.Char(string="Autorizando para tales efectos de manera a")
    show_reports = fields.Boolean(compute='_compute_show_reports')

    def _compute_show_reports(self):
        for r in self:
            if r.create_uid.id != self.env.user.id:
                r.show_reports = False
            else:
                r.show_reports = True


    def reporte_escrito_solicitud(self):
        return self.env.ref('extincion.formato_escrito_solicitud').report_action(self)



    def default_company(self):
        return self.env.user.company_id.id

    institution = fields.Many2one('res.company', string='Institucion',
                                  default=default_company)


    def get_company_name(self):
        company_name = self.env['res.company'].sudo().search([('id', '=', self.institution.id)]).name
        return str(company_name)

    def get_no_iap(self):
        no_iap = self.env['res.company'].sudo().search([('id', '=', self.institution.id)]).partner_id.no_iap
        return str(no_iap)

    def _get_nombreiap(self):
        return self.env.user.company_ids.partner_id.display_name

    nombreiap = fields.Char(default=_get_nombreiap)



    #FUNCION PARA CONCATENAR EL NOMBRE COMPLETO DEL APODERADO
    def _get_nombrecompletoapoderado(self):
        for record in self:
            if bool(record.apoderados_id.segundonombre):
                v_segundonombre = record.apoderados_id.segundonombre
            else:
                v_segundonombre = ''
            if bool(record.apoderados_id.primerapellido):
                v_primerapellido = record.apoderados_id.primerapellido
            else:
                v_primerapellido =''

            if bool(record.apoderados_id.segundoapellido):
                v_segundoapellido = record.apoderados_id.segundoapellido
            else:
                v_segundoapellido =''
            record.nombrecompletoapoderado = record.pnombre +' '+ v_segundonombre+' '+ v_primerapellido +' '+ v_segundoapellido


    #FUNCION PARA ASIGNAR LA IAP EN SESION AL CAMPO SELECTION DE APODERADOS
    def _asignacioniap(self):
        usuario = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        iap = False
        for company in usuario.company_ids:
            iap = company.partner_id
        if iap:
            return int(iap.id)
        else:
            return 0
    num_iap = fields.Integer(default=_asignacioniap)



    # FUNCION PARA MOSTRAR LAS ETAPAS EN LA VISTA KANBAN
    def _get_estatus(self):
        usuario = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])

        for company in usuario.company_ids:
            iap = company.partner_id
            for record in self:
                refidsol = record.id
                filtros = [('RefIdIAP', '=', iap.id), ('RefIdTipoTram', '=', 11), ('RefidSolicitud', '=', refidsol)]
                estatusjap_obj = self.env['tramite.gestion.extincion'].sudo().search(filtros)
                if estatusjap_obj:
                    record.estatusjap = str(estatusjap_obj.EstatusTram)
                else:
                    record.estatusjap = 'Pendiente'


    def _get_asesor(self):
        usuario = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])

        for company in usuario.company_ids:
            iap = company.partner_id
            for record in self:
                refidsol = record.id
                filtros = [('RefIdIAP', '=', iap.id), ('RefIdTipoTram', '=', 11), ('RefidSolicitud', '=', refidsol)]
                asesor_obj = self.env['tramite.gestion.extincion'].sudo().search(filtros)
                if asesor_obj:
                    record.asesortramite = str(asesor_obj.RefIdUsuario.name)
                else:
                    record.asesortramite = 'Pendiente'

        # funcion para obtener los correos del usuario

    def _get_correos(self):
        for record in self:
            user_id = self.env.uid
            usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

            for company in usuario.company_ids:
                iap = company.partner_id

                filtros = [('partner_iap_id', '=', iap.id), ('tipotramite_id', '=', 11)]
                user_obj = self.env['usuarios.tramite'].sudo().search(filtros)
                record.correosavisos = user_obj.user_id.login

    # CORREOS JEFES
    def _get_jefes(self):
        for record in self:
            user_id = self.env.uid
            usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

            for company in usuario.company_ids:
                iap = company.partner_id
                filtros = [('partner_iap_id', '=', iap.id), ('tipotramite_id', '=', 11)]
                jefes_tramite = self.env['jefes.tramite'].sudo().search(filtros)

                records = ''
                for record in jefes_tramite:
                    records += record.user_id.login + ';'

                self.correosavisosjefes = records

    @api.model
    def create(self, vals):
        vals['status'] = 'pendiente'
        return super(solicitud,self).create(vals)

    #Funcion para validacion de archivos pdf
    @api.constrains('attachment','response_to_request_extincion')
    def validation_attachment(self):
        for attachment in self.attachment:
           if pathlib.Path(attachment.name).suffix != '.pdf':
               raise Warning('El archivo ' + attachment.name + ' debe de ser de extension pdf' )
        for response in self.response_to_request_extincion:
           if pathlib.Path(response.name).suffix != '.pdf':
               raise Warning('El archivo ' + response.name + ' debe de ser de extension pdf' )



    def write(self, vals):


        # VALIDA PARA QUE NO SE PUEDA MODIFICAR EL REGISTRO CUANDO ESTE YA FUE ENVIADO POR LA INSTITUCION
        # self:  el argumento self trae todos los campos, con los valores nuevos como si fuera la primera vez
        # self._origin: este objeto trae todos los campos con los valores antiguos
        user_id = self.env.uid  # obtiene el id en sesión

        filtro_solicitud_enviada = [('tipotram', '=', self.tipotram.id),
                                    ('create_uid', '=', user_id),
                                    ('id', '=', self.id)
                                    ]
        solicitudenviado_obj = self.env['tram.sol.extincion'].sudo().search(filtro_solicitud_enviada)

        if solicitudenviado_obj.status == 'enviado':
            raise UserError(('No puede modificar un registro enviado'))
        elif solicitudenviado_obj.status == 'autorizado':
            raise UserError(('Su solicitud ya fue autorizada, motivo por el cual no puede ser modificada'))
        elif solicitudenviado_obj.status == 'rechazado':
            raise UserError(('Su solicitud fue rechazada, por favor verifique con su asesor.'))
        return super(solicitud, self).write(vals)

    @api.onchange('correonotif')
    def validatemail(self):
        if self.correonotif:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.correonotif)
            if match == None:
                raise ValidationError('No es un correo valido')


    # FUNCION PARA ENVIAR EL TRAMITE Y REALIZAR EL REGISTRO A GESTION TRAMITES
    def envio_tramite(self):
        if not self.attachment:
                raise UserError('Es necesario adjuntar la documentación necesaria')
        for record in self:
            user_id = self.env.uid  # OBTIENE EL ID DE SESION DE LA INSTITUCION QUE ESTA INGRESANDO
            # BUSCA EL USUARIO QUE SE ENCUENTRA EN RES_USERS DE LA IAP
            usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

            for company in usuario.company_ids:
                iap = company.partner_id

            # HACE UN SELECT A LA TABLA DE USUARIOS TRAMITE, DONDE LA IAP SEA LA QUE ESTA EN SESION Y EL TIPO DE TRAMITE
            # PARA OBTENER EL USUARIO QUE TIENE ASIGNADO PARA ESE TRAMITE
            filtros = [('partner_iap_id', '=', iap.id), ('tipotramite_id', '=', 11)]
            user_obj = self.env['usuarios.tramite'].sudo().search(filtros)

            # SE HACE EL INSERT A LA TABLA DE GESTION DE TRAMITES
            tramite_gestion_obj = self.env['tramite.gestion.extincion']
            nuevo_registro = {'RefIdIAP': iap.id,
                              'RefIdUsuario': user_obj.user_id.id,
                              'RefIdTipoTram': record.tipotram.id,
                              'EstatusTram': '1',  # 1 : ES LA ETAPA INICIAL DEL TRAMITE
                              'EstatusAsunto': 'activo',
                              'observaciones': '.',
                              'RefidSolicitud': record.id}

            # SE ACTUALIZA EL ESTATUS A ENVIADO EL FOLIO DE LA IAP
            record.write({'status': 'enviado'})

            id_gestion = tramite_gestion_obj.create(nuevo_registro)

            # SE HACE EL SELECT A LA TABA DE TIEMPOS TRAMITE
            tramite_tiempo_obj = self.env['tiempos.tramite.extincion']

            nuevo_registro = {'RefIdGestion': id_gestion.id,
                              'Etapa': 1,
                              'Origen': 1
                              }
            tramite_tiempo_obj.create(nuevo_registro)


            # GESTION DE TRAMIGES GENERAL
            tramite_gestion_obj_GRAL = self.env['tramite.gestion']
            nuevo_registrogral = {'RefIdIAP': iap.id,
                              'RefIdUsuario': user_obj.user_id.id,
                              'RefIdTipoTram': 11,

                              'EstatusAsunto': 'activo',

                              'RefidSolicitud': record.id,
                              'origeningreso': "1"}

            tramite_gestion_obj_GRAL.sudo().create(nuevo_registrogral)


            # MANDA A LLAMAR TEMPLATE PARA EL ENVIO DE CORREO
            template = self.env.ref('extincion.solicitud_correo_extincion')
            template.send_mail(self.id, force_send=True)



    #FUNCION PARA VER LOS TIEMPOS DE REQUERIMIENTO
    def tiempos_tramite(self):
        refidsolicitud = self.id
        #for record in self:
        user_id = self.env.uid  # OBTIENE EL ID DE SESION DE LA INSTITUCION QUE ESTA INGRESANDO
        # BUSCA EL USUARIO QUE SE ENCUENTRA EN RES_USERS DE LA IAP
        usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

        for company in usuario.company_ids:
            refidiap = company.partner_id
            #SI EL FOLIO DE LA IAP ESTA NOTIFICADO,
            filtros = [('RefIdIAP', '=', refidiap.id),
                       ('RefIdTipoTram', '=', self.tipotram.id),
                       ('RefidSolicitud','=',refidsolicitud),
                       ('create_uid','=',user_id)]
            solicitudenviado_obj = self.env['tramite.gestion.extincion'].sudo().search(filtros)
            if solicitudenviado_obj:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Tiempos de la solicitud',
                    'res_model': 'tiempos.tramite.extincion',
                    'res_id': solicitudenviado_obj.id ,
                    'view_mode': 'tree',
                    'view_id': self.env.ref('extincion.tiempos_tramite_tree_view').id,
                    'domain': [('RefIdGestion','=', solicitudenviado_obj.id)],
                    'target': 'new'
                }

#FUNCION PARA VER EL REQUERIMIENTO
    def ver_requerimiento(self):
        requerimiento_obj = self.env['tram.req.extincion'].search([('RefidSolicitud', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'CONTRATOS DE EXTINCIÓN - REQUERIMIENTO',
            'res_model': 'tram.req.extincion',
            'res_id': requerimiento_obj.id if requerimiento_obj else False,
            'view_mode': 'form',
            'view_id': self.env.ref('extincion.requerimiento_IAP_form_view').id,
            'context': {'default_RefidSolicitud': self.id},
            'target': 'current'
        }

    # FUNCION PARA VER EL RESULTADO
    def ver_resultado(self):
        refidsolicitud = self.id

        for record in self:
            user_id = self.env.uid  # OBTIENE EL ID DE SESION DE LA INSTITUCION QUE ESTA INGRESANDO
            # BUSCA EL USUARIO QUE SE ENCUENTRA EN RES_USERS DE LA IAP
            usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

            for company in usuario.company_ids:
                refidiap = company.partner_id
                # SI EL FOLIO DE LA IAP ESTA NOTIFICADO,
                filtros = [('RefIdIAP', '=', refidiap.id),
                           ('RefIdTipoTram', '=', self.tipotram.id),
                           ('RefidSolicitud', '=', refidsolicitud),
                           ('create_uid', '=', user_id)]
                solicitudresultado_obj = self.env['tramite.gestion.extincion'].sudo().search(filtros)
                if solicitudresultado_obj:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Resultado del tramite',
                        'res_model': 'tramite.gestion.extincion',
                        'res_id': solicitudresultado_obj.id if solicitudresultado_obj else False,
                        'view_mode': 'form',
                        'view_id': self.env.ref('extincion.finaliza_tramite_lectura_form_view').id,
                        'context': {'default_RefidSolicitud': self.id},
                        'target': 'current'
                    }

    #FUNCION PARA RESPONDER EL OFICIO DE REQUERIMIENTO
    def responder_requerimiento(self):
        refidsolicitud = self.id

        for record in self:
            if not self.attachment:
                raise UserError('Es necesario adjuntar la documentación necesaria')
            user_id = self.env.uid  # OBTIENE EL ID DE SESION DE LA INSTITUCION QUE ESTA INGRESANDO
            # BUSCA EL USUARIO QUE SE ENCUENTRA EN RES_USERS DE LA IAP
            usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

            for company in usuario.company_ids:
                refidiap = company.partner_id
                #SI EL FOLIO DE LA IAP ESTA NOTIFICADO,
                filtros = [('RefIdIAP', '=', refidiap.id),
                           ('RefIdTipoTram', '=', self.tipotram.id),
                           ('RefidSolicitud','=',refidsolicitud),
                           ('create_uid','=',user_id)]
                solicitudenviado_obj = self.env['tramite.gestion.extincion'].sudo().search(filtros)
                if solicitudenviado_obj:
                    record.write({'status': 'enviado'})
            # MANDA A LLAMAR TEMPLATE PARA EL ENVIO DE CORREO
            template = self.env.ref('extincion.requerimiento_respondido')
            template.send_mail(self.id, force_send=True)


