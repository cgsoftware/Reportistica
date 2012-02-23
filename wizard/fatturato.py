# -*- encoding: utf-8 -*-

import wizard
import decimal_precision as dp
import pooler
import time
from tools.translate import _
from osv import osv, fields
from tools.translate import _



 













class fiscaldoc_fatturato(osv.osv_memory):
    _name = 'fiscaldoc.fatturato'
    _description = 'funzioni stampa ordini jasper'
    _columns = {
                'dadata': fields.date('Da Data Documento', required=True  ),
                'adata': fields.date('A Data Documento', required=True),
                
                #'acliente':fields.many2one('res.partner', 'A cliente', select=True),
                #'danrv': fields.char('Da Documento',size=30,required=True),
                #'anrv': fields.char('A Documento',size=30,required=True),
                'tipodoc':fields.many2one('fiscaldoc.causalidoc', 'Da tipo documento'),
                'atipodoc':fields.many2one('fiscaldoc.causalidoc', 'A tipo documento'),
                #'ordine': fields.selection(  (('T', 'Tipo e Numero Doc'), ('C', 'Cliente'),), 'Tipo di ordinamento', required=True),
                #'group1':fields.boolean('Raggruppo per cliente?'),
                #'group2':fields.boolean('Raggruppo per documento?'),
                #'stampa':fields.boolean('Stampa dettagliata?')
                #'prezzi':fields.boolean('Stampo i prezzi e gli sconti sull''ordine?'),
                #'tipo': fields.selection(  (('O', 'Ordine Cliente'), ('P', 'Preventivo a Cliente')), 'Tipo di docuemento')
                }

    
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        if data['form']['tipodoc']==0 or data['form']['tipodoc']==False:
            data['form']['tipodoc']=1
            data['form']['atipodoc']=99999
        result = {'dadata':data['form']['dadata'],'adata':data['form']['adata'],
                  'agente':data['form']['agente'],
                  'tipodoc':data['form']['tipodoc'],'atipodoc':data['form']['atipodoc'],
                  
                    }
         #funzione di controllo delle variabili 
         # riempie le eventuali lasciate vuote

        #if data['form']['dacliente']==0 or data['form']['dacliente']==False:
        #    data['form']['dacliente']= 1
        #    data['form']['acliente']= 99999
        
            
        return result
      
    def _print_report(self, cr, uid, ids, data, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
        pool = pooler.get_pool(cr.dbname)
        fatture = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])
        Primo = True
        return {
                            'type': 'ir.actions.report.xml',
                            'report_name': 'fatturato',
                            'datas': data,
                            }
            
    def check_report(self, cr, uid, ids, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
            
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['dadata',  'adata',  'tipodoc', 'atipodoc', 'agente'])[0]
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
  
fiscaldoc_fatturato()

class report_prodotto(osv.osv_memory):
    _name = 'report.prodotto'
    _description = 'funzioni stampa ordini jasper'
    _columns = {
                'dadata': fields.date('Da Data Pianificata', required=True  ),
                'adata': fields.date('A Data Pianificata', required=True), 
                'stato': fields.selection([('draft','Draft'),('picking_except', 'Picking Exception'),('confirmed','Waiting Goods'),('ready','Ready to Produce'),('in_production','In Production'),('cancel','Cancelled'),('done','Done')],'Stato', required=True), 
                }
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        parametri = self.browse(cr,uid,ids)[0]
        #import pdb;pdb.set_trace()
        dadatan = time.strptime(parametri.dadata, "%Y-%m-%d")
        dadatan =time.strftime("%d/%m/%Y",dadatan)
        
        adatan = time.strptime(parametri.adata, "%Y-%m-%d")
        adatan =time.strftime("%d/%m/%Y",adatan)
        
        result = {'dadata':parametri.dadata,'adata':parametri.adata, 'data1':dadatan, 'data2':adatan, 
                  'stato':parametri.stato}
        return result

    def _print_report(self, cr, uid, ids, data, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['dadata',  'adata','stato'])[0] #  'tipodoc', 'atipodoc'
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['parameters'] = used_context
        pool = pooler.get_pool(cr.dbname)
        active_ids = context and context.get('active_ids', [])
        
        
        Primo = True
        return {
                            'type': 'ir.actions.report.xml',
                            'report_name': 'prodotto',
                            'datas': data,
                            }
    def check_report(self, cr, uid, ids, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
            
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['dadata',  'adata'])[0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['parameters'] = used_context
        return self._print_report(cr, uid, ids, data, context=context)
    def view_init(self, cr, uid, fields_list, context=None):
        # import pdb;pdb.set_trace()
        res = super(stampa_ordini, self).view_init(cr, uid, fields_list, context=context)

        return res
    def  default_get(self, cr, uid, fields, context=None):
       
        pool = pooler.get_pool(cr.dbname)
        docs = pool.get('mrp.production')
        active_ids = context and context.get('active_ids', [])
        Primo = True
        if active_ids:
             #import pdb;pdb.set_trace()
             for docu in docs.browse(cr, uid, active_ids, context=context):
                if Primo:
                    Primo = False
               
        
        return {}

    
report_prodotto()

               


