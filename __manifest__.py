{
    'name': 'CONTRATOS DE EXTINCIÓN',
    'version': '1.17082022',
    'category': 'TRAMITE DE OBLIGACION - JAPCDMX',
    'sequence': 15,
    'author':'DTIC JAPCDMX',
    'summary': 'Modulo de contratos de extinción',
    'description': 'Modulo de extinción - JAPCDMX',


    'depends': ['base','mail','registroiap'],

    'data': [
        'report/paper_format.xml',
        'report/formato_escrito_solicitud_report.xml',
        'report/formato_escrito_solicitud.xml',
        'report/formato_oficio_requerimiento_report.xml',
        'report/formato_oficio_requerimiento.xml',
        'report/formato_escrito_liquidador_report.xml',
        'report/formato_escrito_liquidador.xml',
        'report/formato_acta_sesion_extincion_report.xml',
        'report/formato_acta_sesion_extincion.xml',
      	'views/solicitud_tramite_view.xml',
        'views/requerimiento_tramite_view.xml',
        'views/ficha_ejecutiva_tramite_view.xml',
        'views/analisis_tramite_view.xml',
        'views/gestion_tramite_view.xml',
        'views/tiempos_tramite_view.xml',
        'views/finaliza_tramite_view.xml',
        'security/tramite_edo_fin_security.xml',
        'security/ir.model.access.csv',
        'datas/template_mail_view.xml',
        'views/menu_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
