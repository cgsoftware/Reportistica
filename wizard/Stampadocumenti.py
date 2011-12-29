# -*- encoding: utf-8 -*-

import wizard
import decimal_precision as dp
import pooler
import time
from tools.translate import _
from osv import osv, fields
from tools.translate import _



class fiscaldoc_brogliacci(osv.osv_memory):
    _name = 'fiscaldoc.brogliacci'
    _description = 'funzioni stampa ordini jasper'
    _columns = {
                'dadata': fields.date('Da Data Documento', required=True  ),
                'adata': fields.date('A Data Documento', required=True),
                'dacliente':fields.many2one('res.partner', 'Da cliente', select=True),
                'acliente':fields.many2one('res.partner', 'A cliente', select=True),
                'danrv': fields.char('Da Documento',size=30,required=True),
                'anrv': fields.char('A Documento',size=30,required=True),
                'tipodoc':fields.many2one('fiscaldoc.causalidoc', 'Da tipo documento'),
                'atipodoc':fields.many2one('fiscaldoc.causalidoc', 'A tipo documento'),
                'ordine': fields.selection(  (('T', 'Tipo e Numero Doc'), ('C', 'Cliente'),), 'Tipo di ordinamento', required=True),
                'group1':fields.boolean('Raggruppo per cliente?'),
                'group2':fields.boolean('Raggruppo per documento?'),
                'stampa':fields.boolean('Stampa dettagliata?')
                #'prezzi':fields.boolean('Stampo i prezzi e gli sconti sull''ordine?'),
                #'tipo': fields.selection(  (('O', 'Ordine Cliente'), ('P', 'Preventivo a Cliente')), 'Tipo di docuemento')
                }

    
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        result = {'dadata':data['form']['dadata'],'adata':data['form']['adata'],
                  'dacliente':data['form']['dacliente'],'acliente':data['form']['acliente'],
                  'tipodoc':data['form']['tipodoc'],'atipodoc':data['form']['atipodoc'],
                  'ordine':data['form']['ordine'], 
                  'group1':data['form']['group1'], 'group2':data['form']['group2']
                    }
         #funzione di controllo delle variabili 
         # riempie le eventuali lasciate vuote

        if data['form']['dacliente']==0 or data['form']['dacliente']==False:
            data['form']['dacliente']= 1
            data['form']['acliente']= 99999
        if data['form']['tipodoc']==0 or data['form']['tipodoc']==False:
            data['form']['tipodoc']=1
            data['form']['atipodoc']=99999
            
        var1 = data['form']['group1']
        var2 = data['form']['group2']
        #import pdb;pdb.set_trace()
       
    
        if var1 == True or var1 == 1:
            if var2 == True or var2 == 1:
                result = {'dadata':data['form']['dadata'],'adata':data['form']['adata'],
                          'dacliente':data['form']['dacliente'],'acliente':data['form']['acliente'],
                          #'danr':data['form']['danrv'],'anr':data['form']['anrv'],
                          'tipodoc':data['form']['tipodoc'],'ordine':data['form']['ordine'], 
                          'atipodoc':data['form']['atipodoc'],'group1':1 , 'group2':1}
            else:
                 result = {'dadata':data['form']['dadata'],'adata':data['form']['adata'],
                          'dacliente':data['form']['dacliente'],'acliente':data['form']['acliente'],
                          #'danr':data['form']['danrv'],'anr':data['form']['anrv'],
                          'tipodoc':data['form']['tipodoc'],'ordine':data['form']['ordine'], 
                          'atipodoc':data['form']['atipodoc'],'group1':1 , 'group2':0}
        else:
             if var2 == True or var2 == 1:
                 result = {'dadata':data['form']['dadata'],'adata':data['form']['adata'],
                           'dacliente':data['form']['dacliente'],'acliente':data['form']['acliente'],
                           #'danr':data['form']['danrv'],'anr':data['form']['anrv'],
                           'tipodoc':data['form']['tipodoc'],'ordine':data['form']['ordine'], 
                          'atipodoc':data['form']['atipodoc'],'group1':0 , 'group2':1}
             else:
                 result = {'dadata':data['form']['dadata'],'adata':data['form']['adata'],
                           'dacliente':data['form']['dacliente'],'acliente':data['form']['acliente'],
                           #'danr':data['form']['danrv'],'anr':data['form']['anrv'],
                           'tipodoc':data['form']['tipodoc'],'ordine':data['form']['ordine'], 
                           'atipodoc':data['form']['atipodoc'], 
                           'group1':0 , 'group2':0}
        return result
      
    def _print_report(self, cr, uid, ids, data, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
        pool = pooler.get_pool(cr.dbname)
        fatture = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])
        Primo = True
        # Quì scelgo il report da lanciare in funzione delle variabili selezionate
        if data['form']['stampa'] == 0 or data['form']['stampa']==False:
            #ORA POSSO STAMPARE SOLO STAMPE SINTETICHE
            if data['form']['group1'] == 1 or data['form']['group1']==True:
                #HA SELEZIONATO IL RAGGRUPPAMENTO PER CLIENTE 
                    return {
                            'type': 'ir.actions.report.xml',
                            'report_name': 'sintetica1',
                            'datas': data,
                            }
            else: # ORDINE PER NUMERO DI DOCUMENTO
                    return {
                            'type': 'ir.actions.report.xml',
                            'report_name': 'sintetica2',
                            'datas': data,
                            }
        else: # STAMPO DETTAGLIATO
            if data['form']['group1'] == 1 or data['form']['group1']==True:
                return {
                            'type': 'ir.actions.report.xml',
                            'report_name': 'dettaglio1', 
                            'datas': data,
                            }
            else:
                return {
                            'type': 'ir.actions.report.xml',
                            'report_name': 'dettaglio2', 
                            'datas': data,
                            }
                

    def check_report(self, cr, uid, ids, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
            
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['dadata',  'adata', 'dacliente' , 'acliente', 'danr', 'anr', 'ordine' , 'group1', 'group2' , 'tipodoc', 'atipodoc','stampa' ])[0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['parameters'] = used_context
        return self._print_report(cr, uid, ids, data, context=context)
    
    def view_init(self, cr, uid, fields_list, context=None):
        # import pdb;pdb.set_trace()
        res = super(stampa_ordini, self).view_init(cr, uid, fields_list, context=context)

        return res
    
             
    def  default_get(self, cr, uid, fields, context=None):
       
        pool = pooler.get_pool(cr.dbname)
        docs = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])
        Primo = True
        if active_ids:
             #import pdb;pdb.set_trace()
             for docu in docs.browse(cr, uid, active_ids, context=context):
                if Primo:
                    Primo = False
        #            DtIni = docu['data_documento']
        #            NrIni = docu['name']
                    danr = docu['id']
                
         #       DtFin = docu['data_documento']
      #          NrFin = docu['name']
                anr = docu['id']                
        
        return {}
  
fiscaldoc_brogliacci()


               


