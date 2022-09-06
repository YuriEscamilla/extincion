from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import datetime


class tramitesgestion(models.Model):
    _name = 'tramite.gestion.extincion'
    _rec_name = 'RefIdTipoTram'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    RefIdIAP = fields.Many2one(string='Nombre de la Institucion', comodel_name='res.partner')
    RefIdUsuario = fields.Many2one(comodel_name='res.users', string='Asesor Asignado', domain=[("id", '=', 'env.uid')])
    RefIdTipoTram = fields.Many2one(comodel_name='cf.tipos.tramites', string='Tramite realizado')
    tipotramite = fields.Many2one(related="RefidSolicitudM.tipotram")
    EstatusTram = fields.Selection([('1', 'Pendiente'),
                                    ('2', 'Análisis'),
                                    ('3', 'Requerimiento'),

                                    ('4', 'Resultado')],
                                   default="1",
                                   string='Estatus de la Solicitud', group_expand='_expand_states')
    EstatusAsunto = fields.Selection([('autorizado', 'Autorizado'),
                                      ('rechazado', 'Rechazado'),
                                      ('activo', 'Activo')])
    # Este campo se comento ya que se requeria una relacion para el formato y no un integer
    # RefidSolicitud = fields.Integer(string='Folio Solicitud')

    RefidSolicitud = fields.Integer(string='Folio Solicitud')
    RefidSolicitudM = fields.Many2one(comodel_name="tram.sol.extincion", compute='_compute_RefidSolicitud')

    @api.depends('RefidSolicitud')
    def _compute_RefidSolicitud(self):
        for r in self:
            RefidSolicitudM = self.env['tram.sol.extincion'].search([('id', '=', r.RefidSolicitud)])
            if RefidSolicitudM:
                r.RefidSolicitudM = RefidSolicitudM
            else:
                r.RefidSolicitudM = False

    fechadocumento = fields.Date(string='Fecha del Oficio')

    observaciones = fields.Text(string="Observaciones del trámite")

    attachment = fields.Many2many('ir.attachment', 'ir_attach_edo_extincion', 'record_relation_edo_extincion',
                                  'attachment_id',
                                  string="Oficio de resultado", tracking=1, required=1)

    formats_asesor = fields.Selection(
        [('written_liquidator ', 'Escrito liquidador bajo protesta de decir la verdad'), ('meeting_minutes',
                                                                                          'Acta sesion extincion de parte')],
        string='¿Que necesitas imprimir?')

    #Formato de escrito liquidador bajo protesta de decir la verdad
    job_title = fields.Char(string="Cuento con título profesional de")
    issued = fields.Char(string="Expedido por la")
    professional_license = fields.Char(string="y cédula profesional número")
    located_in = fields.Char(string="Ubicado en")
    c_c = fields.Char(string="Tal efecto a los CC")
    atentamente = fields.Char(string="Atentamente")


    #Formato de acta de sesion de parte

    hours = fields.Char(string="Horas")
    minutes = fields.Char(string="Minutos")
    day = fields.Char(string="Día")
    month = fields.Char(string="Mes")
    year_session = fields.Char(string="Año")
    located_in_liq = fields.Char(string="Ubicado en")
    session = fields.Char(string="Asumiendo la Presidencia de esta Sesión, el C.")
    position = fields.Char(string="Quién desempeña el cargo de")
    secretary = fields.Char(string="Se designa como Secretario a la C.")
    position_two = fields.Char(string="Quién desempeña el cargo de (2)")
    cumulative_figures = fields.Date(string="Que muestran las cifras acumuladas al")
    cumulative_figures_two = fields.Date(string="Que muestran las cifras acumuladas al (2)")
    order_two = fields.Char(string="El (la)")
    cumulative_figures_tree = fields.Date(string="Una copia de los estados financieros que muestran las cifras acumuladas al")
    votes = fields.Char(string="Los aprueban en sus términos, por lo que, por")
    cumulative_figures_four = fields.Date(string="Se aprueban los estados financieros que muestran las cifras acumuladas al")
    president_session = fields.Char(string="El Presidente de la Sesión")
    justify_session = fields.Text(string="Justificación de la extinción")
    president_session_point_four = fields.Char(string="En desahogo del cuarto punto del orden del día, el Presidente de la Sesión")
    liquidator_design = fields.Char(string="Se propone designar como liquidador por parte de ésta a")
    appointed_liquidator = fields.Char(string="Se designa como liquidador a") #Checar si hay que cambiar el string
    president_session_point_five = fields.Char(string="En desahogo del quinto punto del Orden del Día, el Presidente de la Sesión")
    delegates = fields.Char(string="Se designa al (los)")
    six_point = fields.Char(string="En desahogo del sexto punto del orden del día, el Presidente de la Sesión")
    address_notif = fields.Char(string="El inmueble ubicado en")
    c_c_session = fields.Char(string="Para tales efectos al (los) (C.C)")
    hours_two = fields.Char(string="Horas (2)")
    minutes_two = fields.Char(string="Minutos (2)")
    final_assist = fields.Date(string="Fecha de asistencia final")
    name_and_sign_one = fields.Char(string="Nombre y firma (1)")
    name_and_sign_two = fields.Char(string="Nombre y firma (2)")
    name_and_sign_tree = fields.Char(string="Nombre y firma (3)")
    name_and_sign_four = fields.Char(string="Nombre y firma (4)")
    name_and_sign_five = fields.Char(string="Nombre y firma (5)")
    name_and_sign_six = fields.Char(string="Nombre y firma (6)")


    def reporte_escrito_liquidador(self):
        return self.env.ref('extincion.formato_escrito_liquidador').report_action(self)

    def reporte_acta_sesion_extincion(self):
        return self.env.ref('extincion.formato_acta_sesion_extincion').report_action(self)


    def _get_year(self):
        return date.today().year

    year = fields.Char(string="Año en curso", default=_get_year)

    # ABRE SOLICITUD
    def abrir_folio(self):
        tipotram = self.RefIdTipoTram.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'CONTRATOS DE EXTINCIÓN',
            'res_model': 'tram.sol.extincion',
            'res_id': self.RefidSolicitud,
            'view_mode': 'form',
            'view_id': self.env.ref('extincion.solicitud_form_view').id,
            'context': {'default_create_uid': self.RefIdIAP},
            'target': 'current'
        }

    # ABRE OFICIO DE REQUERIMIENTO
    def requerimientoventana(self):
        idtram = self.RefIdTipoTram.id
        print(idtram)

        requerimiento_obj = self.env['tram.req.extincion'].search([('RefidSolicitud', '=', self.RefidSolicitud)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'CONTRATOS DE EXTINCIÓN - REQUERIMIENTO',
            'res_model': 'tram.req.extincion',
            'res_id': requerimiento_obj.id if requerimiento_obj else False,
            'view_mode': 'form',
            'view_id': self.env.ref('extincion.requerimiento_form_view').id,
            'context': {'default_RefidSolicitud': self.RefidSolicitud},
            'target': 'current'
        }

    def analisis(self):
        idtram = self.RefIdTipoTram.id
        print(idtram)

        # SE CREA REQUERIMIENTO_OBJ CON EL ID DEL FOLIO SELECCIONADO EN KANBAN
        analisis_obj = self.env['tram.ana.extincion'].search([('RefidSolicitud', '=', self.RefidSolicitud)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Analisis del tramite',
            'res_model': 'tram.ana.extincion',
            'res_id': analisis_obj.id if analisis_obj else False,
            'view_mode': 'form',
            'view_id': self.env.ref('extincion.analisistramite_form_view').id,
            'context': {'default_RefidSolicitud': self.RefidSolicitud},
            'target': 'current'
        }

        # ABRE FICHA EJECUTIVA

    def ficha_ejecutiva(self):
        try:
            idtram = self.RefIdTipoTram.id
            refidsolicitud = self.RefidSolicitud
            print(idtram)
            print(refidsolicitud)
            # SI EL TIPO DE TRAMITE ES EL "BASE"
            if idtram == 1:
                ficha_obj = self.env['tram.fichaejecutiva.extincion'].search(
                    [('RefidSolicitud', '=', self.RefidSolicitud)])
                if not ficha_obj:
                    createficha_objt = self.env['tram.fichaejecutiva.extincion']
                    ficha_obj = createficha_objt.create({'RefidSolicitud': self.RefidSolicitud})
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Ficha Ejecutiva EXTINCIÓN',
                    'res_model': 'tram.fichaejecutiva.extincion',
                    'res_id': ficha_obj.id if ficha_obj else False,
                    'view_mode': 'form',
                    'view_id': self.env.ref('extincion.ficha_tramite_form_view').id,
                    'context': {'default_RefidSolicitud': self.RefidSolicitud},
                    'target': 'current'
                }
        except Exception as e:
            raise UserError(e)

    # ABRE RESULTADO
    def resultado(self):
        idtram = self.RefIdTipoTram
        return {
            'type': 'ir.actions.act_window',
            'name': 'FINALIZA TRAMITE CONTRATOS DE EXTINCIÓN',
            'res_model': 'tramite.gestion.extincion',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('extincion.finaliza_tramite_form_view').id,
            'target': 'current'
        }

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).EstatusTram.selection]

    def write(self, vals):

        if 'EstatusTram' in vals:
            origen = (self.EstatusTram)
            nueva_etapa = vals['EstatusTram']
            if nueva_etapa < origen:
                raise UserError(('No puede regresar a una etapa anterior'))
            else:
                tramite_tiempo_obj = self.env['tiempos.tramite.extincion']
                nuevo_registro = {'RefIdGestion': self.id,
                                  'Etapa': nueva_etapa,
                                  'Origen': origen
                                  }
                tramite_tiempo_obj.create(nuevo_registro)
                return super(tramitesgestion, self).write(vals)
        else:
            return super(tramitesgestion, self).write(vals)

    def autorizado(self):
        idtram = self.RefIdTipoTram.id
        if not self.attachment:
            raise UserError('Es necesario adjuntar la documentación necesaria para autorizacion ')
        # se autoriza en automatico el campo de la tabla tramite.gestion.base
        self.EstatusAsunto = 'autorizado'

        # se autoriza el campo de la tabla de gestion general
        filtros_gral = [('RefidSolicitud', '=', self.RefidSolicitud), ('RefIdTipoTram', '=', 11)]
        tramite_gestion_obj_GRAL = self.env['tramite.gestion'].sudo().search(filtros_gral)

        if tramite_gestion_obj_GRAL:
            actualiza_estatus = {'EstatusAsunto': 'autorizado'}
            tramite_gestion_obj_GRAL.write(actualiza_estatus)

        # se autoriza el folio de la solicitud
        filtros = [('id', '=', self.RefidSolicitud), '|', ('status', '=', 'enviado'), ('status', '=', 'notificado')]
        folio_obj = self.env['tram.sol.extincion'].sudo().search(filtros)
        # SE ACTUALIZA EL ESTATUS A ENVIADO EL FOLIO DE LA IAP EXTINCIÓN
        folio_obj.status = 'autorizado'

        # MANDA A LLAMAR TEMPLATE PARA EL ENVIO DE CORREO
        template = self.env.ref('extincion.solicitud_correo_extincion_termino')
        template.send_mail(self.id, force_send=True)

        return {"view_mode": "kanban",
                "res_model": "tramite.gestion.extincion",
                "type": "ir.actions.act_window",
                "target": "main",
                "name": _('CONTRATOS DE EXTINCIÓN'),
                "view_id": self.env.ref('extincion.solicitudes_tramite_kanban_view').id,
                "context": {'search_default_activo': 1}}

    def cancelado(self):
        idtram = self.RefIdTipoTram.id
        if not self.attachment:
            raise UserError('Es necesario adjuntar la documentación necesaria para el rechazo ')

        # se autoriza en automatico el campo de la tabla de tramite.gestion.base
        self.EstatusAsunto = 'rechazado'

        # se autoriza el campo de la tabla de gestion general
        filtros_gral = [('RefidSolicitud', '=', self.RefidSolicitud), ('RefIdTipoTram', '=', 11)]
        tramite_gestion_obj_GRAL = self.env['tramite.gestion'].sudo().search(filtros_gral)

        if tramite_gestion_obj_GRAL:
            actualiza_estatus = {'EstatusAsunto': 'rechazado'}
            tramite_gestion_obj_GRAL.write(actualiza_estatus)

        # se autoriza el folio de la solicitud
        filtros = [('id', '=', self.RefidSolicitud), '|', ('status', '=', 'enviado'), ('status', '=', 'notificado')]
        folio_obj = self.env['tram.sol.extincion'].sudo().search(filtros)
        # SE ACTUALIZA EL ESTATUS A ENVIADO EL FOLIO DE LA IAP
        folio_obj.status = 'rechazado'

        # MANDA A LLAMAR TEMPLATE PARA EL ENVIO DE CORREO
        template = self.env.ref('extincion.solicitud_correo_extincion_termino')
        template.send_mail(self.id, force_send=True)

        return {"view_mode": "kanban",
                "res_model": "tramite.gestion.extincion",
                "type": "ir.actions.act_window",
                "target": "main",
                "name": _('CONTRATOS DE EXTINCIÓN'),
                "view_id": self.env.ref('extincion.solicitudes_tramite_kanban_view').id,
                "context": {'search_default_activo': 1}}
