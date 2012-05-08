# -*- encoding: utf-8 -*-

import wizard
import decimal_precision as dp
import pooler
import time
from tools.translate import _
from osv import osv, fields
from tools.translate import _
import base64

class tempstatistiche_brogliacci(osv.osv):
    def _pulisci(self,cr,uid,context):
        ids = self.search(cr,uid,[])
        ok = self.unlink(cr,uid,ids,context)
        return True
    
    _name ='tempstatistiche.brogliacci'
    _description = 'temporaneo per la stampa dei brogliacci'
    _columns = {#'documento':fields.many2one('fiscaldoc.header', 'Numero Documento'),
                'imponibile':fields.float('Imponibile', digits=(16, 4)),
                'imposta':fields.float('Imposta', digits=(16, 4)),
                'totale':fields.float('Totale', digits=(16, 4)),
                'conai':fields.float('Conai', digits=(16, 4)),
                'documento':fields.float('Conai', digits=(16, 4)),
                                          
                }
    
    def carica_doc(self, cr,uid,parametri,context):
        #import pdb;pdb.set_trace()
        ok = self._pulisci(cr, uid, context)
        testa_obj = self.pool.get('fiscaldoc.header')
        partner_obj = self.pool.get('res.partner')
        conai = self.pool.get('conai.castelletto')
        #filtro1 = [('tipo_documento', 'in', ('FA','FI','FD','NC'))] #AGGIUNGERE NOTE CREDITO E NOTE DEBITO
        #idsTipoDoc = self.pool.get('fiscaldoc.causalidoc').search(cr, uid, filtro1)
        #idsTipoDoc = tuple(idsTipoDoc)
        if parametri.agente:
            filtro_ag =[('agent_id','=',parametri.agente.id)]
            partner_ids = partner_obj.search(cr, uid, filtro_ag)
            partner_ids = tuple(partner_ids)
            filtro2 = [('partner_id', 'in', partner_ids),('data_documento','<=',parametri.adata ),('data_documento','>=', parametri.dadata )]
        elif parametri.dacliente:
            filtro2 = [('data_documento','<=',parametri.adata ),('data_documento','>=', parametri.dadata ), ('partner_id', '=', parametri.dacliente.id)]
        elif parametri.tipodoc:
            filtro2 = [('data_documento','<=',parametri.adata ),('data_documento','>=', parametri.dadata ), ('tipo_doc', '=', parametri.tipodoc.id)]
        else:
            filtro2 = [('data_documento','<=',parametri.adata ),('data_documento','>=', parametri.dadata )]
        
        doc = testa_obj.search(cr, uid, filtro2)
        
        if doc:
            for documento in testa_obj.browse(cr, uid, doc):
                cerca = [('name', '=', documento.id)]
                righe_conai = conai.search(cr, uid, cerca)
                tot = 0
                if righe_conai:
                    #import pdb;pdb.set_trace()
                    for riga in conai.browse(cr,uid, righe_conai):
                        
                        tot += riga.totale_conai
                if documento.tipo_doc.tipo_operazione == 'C':
                 if not documento.differita_id:
                 #import pdb;pdb.set_trace()
                  if documento.tipo_doc.tipo_documento == 'NC':
                    
                    rigawr={'documento': documento.id,
                            'totale': documento.totale_documento * -1,
                            'imposta': documento.totale_imposta * -1,
                            'imponibile': documento.totale_imponibile * -1,
                            'conai':tot*-1
                            }
                    ok = self.create(cr, uid, rigawr)
                  else:
                    riga={'documento': documento.id,
                            'totale': documento.totale_documento,
                            'imposta': documento.totale_imposta,
                            'imponibile': documento.totale_imponibile,
                            'conai':tot}                            
                    ok = self.create(cr, uid, riga)
        return True
    
                    
        
        

tempstatistiche_brogliacci()


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
                'stampa':fields.boolean('Stampa dettagliata?'),
                'export_csv':fields.boolean('Genera CSV'),
                'agente':fields.many2one('sale.agent', 'Agente', select=True),
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
                  'group1':data['form']['group1'], 'group2':data['form']['group2'],
                  'agente':data['form']['agente'],
                    }
         #funzione di controllo delle variabili 
         # riempie le eventuali lasciate vuote
        
        if data['form']['dacliente']==0 or data['form']['dacliente']==False:
            data['form']['dacliente']= 1
            
        if data['form']['tipodoc']==0 or data['form']['tipodoc']==False:
            data['form']['tipodoc']=1
            data['form']['atipodoc']=99999
        data['form']['acliente']= 0    
        var1 = data['form']['group1']
        var2 = data['form']['group2']
        
        parametri = self.browse(cr,uid,ids)[0]
        #import pdb;pdb.set_trace()
        if parametri.agente:
            data['form']['agente']=parametri.agente.id
        else:
             data['form']['agente']= 0  
       
    
        if var1 == True or var1 == 1:
            if var2 == True or var2 == 1:
                result = {'dadata':data['form']['dadata'],'adata':data['form']['adata'],
                          'dacliente':data['form']['dacliente'],'acliente':data['form']['acliente'],
                          #'danr':data['form']['danrv'],'anr':data['form']['anrv'],
                          'tipodoc':data['form']['tipodoc'],'ordine':data['form']['ordine'], 'agente':data['form']['agente'],
                          'atipodoc':data['form']['atipodoc'],'group1':1 , 'group2':1}
            else:
                 result = {'dadata':data['form']['dadata'],'adata':data['form']['adata'],
                          'dacliente':data['form']['dacliente'],'acliente':data['form']['acliente'],'agente':data['form']['agente'],
                          #'danr':data['form']['danrv'],'anr':data['form']['anrv'],
                          'tipodoc':data['form']['tipodoc'],'ordine':data['form']['ordine'], 
                          'atipodoc':data['form']['atipodoc'],'group1':1 , 'group2':0}
        else:
             if var2 == True or var2 == 1:
                 result = {'dadata':data['form']['dadata'],'adata':data['form']['adata'],
                           'dacliente':data['form']['dacliente'],'acliente':data['form']['acliente'],'agente':data['form']['agente'],
                           #'danr':data['form']['danrv'],'anr':data['form']['anrv'],
                           'tipodoc':data['form']['tipodoc'],'ordine':data['form']['ordine'], 
                          'atipodoc':data['form']['atipodoc'],'group1':0 , 'group2':1}
             else:
                 result = {'dadata':data['form']['dadata'],'adata':data['form']['adata'],
                           'dacliente':data['form']['dacliente'],'acliente':data['form']['acliente'],'agente':data['form']['agente'],
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
        data['form'] = self.read(cr, uid, ids, ['dadata', 'agente', 'adata', 'dacliente' , 'acliente', 'danr', 'anr', 'ordine' , 'group1', 'group2' , 'tipodoc', 'atipodoc','stampa' ])[0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['parameters'] = used_context
        parametri = self.browse(cr,uid,ids)[0]
        ok = self.pool.get('tempstatistiche.brogliacci').carica_doc(cr,uid,parametri,context)
        if parametri.export_csv:
            return  {
                             'name': 'Export Brogliacci',
                             'view_type': 'form',
                             'view_mode': 'form',
                             'res_model': 'crea_csv_brogliacci',
                             'type': 'ir.actions.act_window',
                             'target': 'new',
                             'context': context                            
                             
                             }
        else:
            return self._print_report(cr, uid, ids, data, context=context)
    
        return
    
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

class crea_csv_brogliacci(osv.osv_memory):
    _name = "crea_csv_brogliacci"
    _description = "Crea il csv dal temp. Inventario"
    _columns = {
                    'state': fields.selection((('choose', 'choose'), # choose accounts
                                               ('get', 'get'), # get the file
                                   )),
                    #'nomefile':fields.char('Nome del file',size=20,required = True)
                    'data': fields.binary('File', readonly=True),

                    }   
                 
    _defaults = {
                 'state': lambda * a: 'choose',
                 }
    def generacsvbrog(self, cr, uid, ids,context=None): 
        testa_obj = self.pool.get('fiscaldoc.header')
        data= 0
        if ids:
            #import pdb;pdb.set_trace()
            idts = self.pool.get('tempstatistiche.brogliacci').search(cr,uid,[], order='documento', context=context)
            if idts:
                File = """"""""
                Record =""
                Record += '"'+"Tipo"+'";'
                Record += '"'+"Data Documento"+'";'
                Record += '"'+"Documento"+'";'
                Record += '"'+"Cliente"+'";'
                Record += '"'+"Agente"+'";'
                Record += '"'+"Pagamento"+'";'
                Record += '"'+"Imponibile"+'";'
                Record += '"'+"Imposta"+'";'
                Record += '"'+"Conai"+'";' 
                Record += '"'+"Totale"+'";'
                Record += "\r\n"
                for riga in self.pool.get('tempstatistiche.brogliacci').browse(cr,uid,idts,context):
                    #Record =""
                    doc = testa_obj.search(cr, uid, [('id','=', riga.documento)])
                    #import pdb;pdb.set_trace()
                    if doc:
                        Record += '"'+ testa_obj.browse(cr, uid, doc[0]).tipo_doc.name+'";'
                        data = testa_obj.browse(cr, uid, doc[0]).data_documento
                        data = time.strptime(data, "%Y-%m-%d")
                        data = time.strftime("%d/%m/%Y",data)
                        Record += '"'+ data +'";'
                        Record += '"'+ testa_obj.browse(cr, uid, doc[0]).name+'";'
                        Record += '"'+ testa_obj.browse(cr, uid, doc[0]).partner_id.name +'";'
                        Record += '"'+ testa_obj.browse(cr, uid, doc[0]).partner_id.agent_id.name+'";'
                        Record += '"'+ testa_obj.browse(cr, uid, doc[0]).pagamento_id.name+'";'
                    else:
                        Record += '"'+'";'
                        Record += '"'+'";'
                        Record += '"'+'";'
                        Record += '"'+'";'
                        Record += '"'+'";'
                        Record += '"'+'";'
                    Record += '"'+ str(riga.imponibile)+'";'
                    Record += '"'+ str(riga.imposta)+'";'
                    Record += '"'+ str(riga.conai)+'";'
                    Record += '"'+ str(riga.totale)+'";'
                    Record += "\r\n"
                #import pdb;pdb.set_trace()
                File += Record
                out = base64.encodestring(File)
                return self.write(cr, uid, ids, {'state':'get', 'data':out}, context=context)
        else:
            return {'type': 'ir.actions.act_window_close'}
                
crea_csv_brogliacci()
               


