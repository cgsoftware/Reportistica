# -*- encoding: utf-8 -*-

import wizard
import decimal_precision as dp
import pooler
import time
from tools.translate import _
from osv import osv, fields
from tools.translate import _
import base64

class tempstatistiche_ordinato(osv.osv):
    
    def _pulisci(self,cr,uid,context):
        ids = self.search(cr,uid,[])
        ok = self.unlink(cr,uid,ids,context)
        return True
    
    _name='tempstatistiche.ordinato'
    _description = 'Temporaneo ordini in evasione'
    _columns = {'riga':fields.many2one('sale.order.line', 'Ordine', required=True),
                'evasa':fields.float('Q.tà Evasa', digits=(12,3)),
                'daevadere':fields.float('Q.tà da Evadere', digits=(12,3)),
                'categoria':fields.char('categoria',size=64)
                }
    
    
    def nome_categoria(self, cr,uid,categoria,context):
       #import pdb;pdb.set_trace()  
       nome_cat =''
       continua = True
       if categoria:
        while continua:
           if categoria.parent_id:
               categoria = categoria.parent_id
           else:
                nome_cat = categoria.name
                continua=False
        
       return nome_cat
    
    
    
    
    
    def mappa_categoria(self, cr, uid, categoria, context):
        lista_id=[]
       
        for categ in categoria.categoria_ids: 
            lista_id.append(categ.categoria.id)
            #import pdb;pdb.set_trace()
            if categ.categoria.child_id:
                for child in categ.categoria.child_id:
                    lista_id.append(child.id)
                    if child.child_id:
                        for figlio in child.child_id:
                            lista_id.append(figlio.id)
                    
                    
        
        return lista_id
     
    def carica_doc(self,cr,uid,parametri,context):
        #
        ok = self._pulisci(cr, uid, context)
        sale = self.pool.get('sale.order')
        filtro_data = [('date_order','<=', parametri.adata),('date_order','>=', parametri.dadata)]
        #filtro_data = [('name','=','CO0000083-2012')]
        ord_ids = sale.search(cr, uid, filtro_data)
        if ord_ids:
            #ho gli id degli ordini nel range di date
            lista_id=[]
            if parametri.categoria_ids:
                #HO UNA CATEGORIA DA INCLUDERE
                lista_id = self.mappa_categoria(cr, uid, parametri, context)
            for ordine in sale.browse(cr, uid, ord_ids):
              #import pdb;pdb.set_trace()
              if not ordine.chiuso:
                #cerca = [('id','=',ordine.id)]
                #id_temp = self.search(cr,uid,cerca)
               if ordine.order_line:
                for riga_doc in ordine.order_line:
                    #adesso leggo le righe dell'ordine selezionato
		 if riga_doc.product_id:

                    if riga_doc.product_id.product_tmpl_id.categ_id.id in lista_id:                        
                        if riga_doc.move_ids:
                         
                         
                         for stock in riga_doc.move_ids:
                                                 
                                           
                           if parametri.evase==1 or parametri.evase == True : 
                              #DEVE STAMPARE ANCHE LE RIGHE GIA' EVASE      
                              if stock.state == 'done':
                                  evasa=stock.product_qty,
                                  if stock.product_qty <= riga_doc.product_uom_qty:
                                      cerca=[('riga','=',stock.sale_line_id.id)]
                                      id_temp = self.search(cr,uid,cerca)
                                      if id_temp:
                                       #import pdb;pdb.set_trace()
                                       riga_temp=self.browse(cr,uid, id_temp[0])
                                       rigawr={'evasa':riga_temp.evasa+stock.product_qty,
                                           'daevadere':riga_temp.daevadere-stock.product_qty
                                              }
                                       ok = self.write(cr,uid,id_temp,rigawr)
                                       
                                      else:
                                       categoria  = riga_doc.product_id.product_tmpl_id.categ_id 
                                       cat_name = self.nome_categoria(cr, uid, categoria, context)   
                                       rigawr={'riga':riga_doc.id,
                                              'evasa':evasa[0],
                                              'daevadere':riga_doc.product_uom_qty-evasa[0],
                                              'categoria': cat_name
                                              }
                                      
                                       ok = self.create(cr,uid,rigawr)
                                  else:
                                      categoria  = riga_doc.product_id.product_tmpl_id.categ_id 
                                      cat_name = self.nome_categoria(cr, uid, categoria, context)
                                      rigawr={'riga':riga_doc.id,
                                              'evasa':stock.product_qty,
                                              'daevadere':0,
                                              'categoria': cat_name
                                              }
                                      ok = self.create(cr,uid,rigawr)
                              else:
                                  evasa0=0
                                  categoria  = riga_doc.product_id.product_tmpl_id.categ_id 
                                  cat_name = self.nome_categoria(cr, uid, categoria, context)
                                  rigawr={'riga':riga_doc.id,
                                          'evasa':evasa0,
                                          'daevadere':riga_doc.product_uom_qty,
                                          'categoria': cat_name
                                          }
                                  ok = self.create(cr,uid,rigawr)
                           else:
                              #SOLO RIGHE DA EVADERE
                              #
                              if stock.state == 'done':
                                  
                                  
                                  
                                   evasa=stock.product_qty,
                                   if stock.product_qty <= riga_doc.product_uom_qty:
                                    cerca=[('riga','=',stock.sale_line_id.id)]
                                    id_temp = self.search(cr,uid,cerca)
                                    if id_temp:
                                       #import pdb;pdb.set_trace()
                                       riga_temp=self.browse(cr,uid, id_temp[0])
                                       rigawr={'evasa':riga_temp.evasa+stock.product_qty,
                                           'daevadere':riga_temp.daevadere-stock.product_qty
                                              }
                                       if riga_temp.daevadere-stock.product_qty>0:
                                          ok = self.write(cr,uid,id_temp,rigawr)
                                       else:
                                
                                          rigawr={}
                                    else:
                                      categoria  = riga_doc.product_id.product_tmpl_id.categ_id 
                                      cat_name = self.nome_categoria(cr, uid, categoria, context)  
                                      rigawr={'riga':riga_doc.id,
                                              'evasa':evasa[0],
                                              'daevadere':riga_doc.product_uom_qty-evasa[0],
                                              'categoria': cat_name
                                              }
                                      if riga_doc.product_uom_qty-evasa[0]>0:
                                          ok = self.create(cr,uid,rigawr)
                                      else:
                                          rigawr={}
                              else:
                                   categoria  = riga_doc.product_id.product_tmpl_id.categ_id 
                                   cat_name = self.nome_categoria(cr, uid, categoria, context)
                                   rigawr={'riga':riga_doc.id,
                                          'evasa':0,
                                          'daevadere':riga_doc.product_uom_qty,
                                          'categoria': cat_name
                                              }
                                   ok = self.create(cr,uid,rigawr)
                              
                                 
                                      
                                      
        return 
                    
                        
         
         
    
tempstatistiche_ordinato()

class stampa_ordinato(osv.osv_memory):
    _name = 'stampa.ordinato'
    _description = 'funzioni stampa ordini jasper'
    _columns = {
                'dadata': fields.date('Da Data Documento', required=True  ),
                'adata': fields.date('A Data Documento', required=True),
                'categoria_ids':fields.one2many('parcalcolo.categorie.order', 'name', 'Categorie da Includere', required=True),
                'evase': fields.boolean('Stampo anche le righe evase?',required=True),
                'stampa':fields.selection([('html','HTML'),('csv','CSV'),('rtf','RTF'),('odt','ODT'),('ods','ODS'),('txt','Text'),('pdf','PDF')], 'File di Stampa'),
                'export_csv':fields.boolean('Genera CSV')
                #'dacliente':fields.many2one('res.partner', 'Da cliente', select=True),
                #'acliente':fields.many2one('res.partner', 'A cliente', select=True),
                #'danrv': fields.char('Da Documento',size=30,required=True),
                #'anrv': fields.char('A Documento',size=30,required=True),
                #'tipodoc':fields.many2one('fiscaldoc.causalidoc', 'Da tipo documento'),
                #'atipodoc':fields.many2one('fiscaldoc.causalidoc', 'A tipo documento'),
                #'ordine': fields.selection(  (('T', 'Tipo e Numero Doc'), ('C', 'Cliente'),), 'Tipo di ordinamento', required=True),
                #'group1':fields.boolean('Raggruppo per cliente?'),
                #'group2':fields.boolean('Raggruppo per documento?'),
                #'stampa':fields.boolean('Stampa dettagliata?')
                #'prezzi':fields.boolean('Stampo i prezzi e gli sconti sull''ordine?'),
                #'tipo': fields.selection(  (('O', 'Ordine Cliente'), ('P', 'Preventivo a Cliente')), 'Tipo di docuemento')
                }
    _defaults = { 'stampa':lambda * a: 'PDF',}
    
    def _build_contexts(self, cr, uid, ids, data, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
        result = {}
            
        result = {}
        parametri = self.browse(cr,uid,ids)[0]
        data1 = time.strptime(parametri.dadata, "%Y-%m-%d")
        data1 =time.strftime("%d/%m/%Y",data1)
        
        data2 = time.strptime(parametri.adata, "%Y-%m-%d")
        data2 =time.strftime("%d/%m/%Y",data2)
        nome_cat =''
        #import pdb;pdb.set_trace()
        for categ in parametri.categoria_ids:
            nome_cat += categ.categoria.name
            nome_cat += '-'
        result = {'dadata':data1,'adata':data2, 'categoria':nome_cat, 'evase':parametri.evase }
	return result
      

    def _print_report(self, cr, uid, ids, data, parametri, context=None):
       
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['dadata',  'adata','categoria_ids', 'evase'])[0] #  'tipodoc', 'atipodoc' 
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['parameters'] = used_context
        pool = pooler.get_pool(cr.dbname)
        active_ids = context and context.get('active_ids', [])
        #
        #data['jasper_output'] = parametri.stampa
        #
        report = self.pool.get('ir.actions.report.xml')
        nome = 'ordinato'
        filtro =[('report_name','=', nome)]
        report_id = report.search(cr, uid, filtro)
        stampa = { 'jasper_output': parametri.stampa, 'report_type':parametri.stampa }
        riga = report.browse(cr, uid, report_id)[0]
	#import pdb;pdb.set_trace()        
	#riga.jasper_output = parametri.stampa
        #riga.report_type = parametri.stampa
        #ok = self.write(cr,uid,report_id,stampa)
        #id =
        ok = riga.write(stampa)
	
	#jasper_report.register_jasper_report( report.report_name, report.model )
        return {'type': 'ir.actions.report.xml',
                'report_name': 'ordinato',
                'datas': data,
                
                }
                

    def check_report(self, cr, uid, ids, context=None):
        #
        if context is None:
            context = {}
            
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['dadata',  'adata'])[0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['parameters'] = used_context
        parametri = self.browse(cr,uid,ids)[0]
        if parametri.export_csv:
            return  {
                             'name': 'Export Ordinato',
                             'view_type': 'form',
                             'view_mode': 'form',
                             'res_model': 'crea_csv_ordinato',
                             'type': 'ir.actions.act_window',
                             'target': 'new',
                             'context': context                            
                             
                             }
        else:
            return self._print_report(cr, uid, ids, data, parametri, context=None)
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
    
    def crea_temp(self, cr, uid, ids, data, context=None):
        parametri = self.browse(cr,uid,ids)[0]
        ok = self.pool.get('tempstatistiche.ordinato').carica_doc(cr,uid,parametri,context)
        
        #import pdb;pdb.set_trace()
        return self.check_report(cr, uid, ids, context=None)
  
stampa_ordinato()

class parcalcolo_categorie_order(osv.osv_memory):
    _name = 'parcalcolo.categorie.order' 
    _description = 'parametri di selezione categorie da escludere'
    _columns = {'name':fields.many2one('stampa.ordinato','Testata parametri'),
                'categoria':fields.many2one('product.category', 'Categorie da includere', required=True,),
                }
parcalcolo_categorie_order()

class sale_order(osv.osv):
    _inherit = 'sale.order' 
    _columns = {'chiuso':fields.boolean('Considera Evaso', required=False),
                }
sale_order()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
                'sale_line_id': fields.many2one('sale.order.line', 'Sales Order Line', ondelete='set null', select=True, readonly=False),
    }
    
    
class crea_csv_ordinato(osv.osv_memory):
    _name = "crea_csv_ordinato"
    _description = "Crea il csv dal temp. ordinato"
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
    
    def generacsvordinato(self, cr, uid, ids,context=None):
        order_obj = self.pool.get('sale.order')
        if ids:            
            idts = self.pool.get('tempstatistiche.ordinato').search(cr,uid,[])
            if idts:
                #import pdb;pdb.set_trace()
                File = """"""""
                Record =""
                Record += '"'+"Ordine"+'";'
                Record += '"'+"Data Ordine"+'";'
                Record += '"'+"Cliente"+'";'
                Record += '"'+"Agente"+'";'
                Record += '"'+"Articolo"+'";'
                Record += '"'+"Categoria"+'";'
                Record += '"'+"U.M."+'";'
                Record += '"'+"Q.ta' Ordinata"+'";'
                Record += '"'+"Peso Conai"+'";'
                Record += '"'+"Q.ta' in Kg"+'";'
                Record += '"'+"Prezzo unitario"+'";'
                Record += '"'+"Importo"+'";'
                Record += '"'+"Q.ta' Evasa"+'";'
                Record += '"'+"Q.ta' Da Evadere"+'";'
                Record += '"'+"Importo da Evadere"+'";'
                Record += '"'+"Giorni di consegna"+'";'
                Record += "\r\n"
                for riga in self.pool.get('tempstatistiche.ordinato').browse(cr,uid,idts, context):
                    #import pdb;pdb.set_trace()
                    Record += '"'+ riga.riga.order_id.name+'";'
                    data = riga.riga.order_id.date_order
                    data = time.strptime(data, "%Y-%m-%d")
                    data = time.strftime("%d/%m/%Y",data)
                    Record += '"'+ data +'";'
                    Record += '"'+ riga.riga.order_id.partner_id.name +'";'
                    Record += '"'+ riga.riga.order_id.partner_id.agent_id.name +'";'
                    Record += '"'+ riga.riga.product_id.name +'";'
                    Record += '"'+ riga.categoria +'";'
                    Record += '"'+ riga.riga.product_uom.name+'";'
                    Record += '"'+ str(riga.riga.product_uom_qty)+'";'
                    Record += '"'+ str(riga.riga.product_id.peso_prod)+'";'
                    Record += '"'+ str(riga.riga.product_uom_qty*riga.riga.product_id.peso_prod)+'";'
                    Record += '"'+ str(riga.riga.price_unit)+'";'
                    Record += '"'+ str(riga.riga.price_subtotal)+'";'
                    Record += '"'+ str(riga.evasa)+'";'
                    Record += '"'+ str(riga.daevadere)+'";'
                    Record += '"'+ str(riga.daevadere*riga.riga.price_unit)+'";'
                    Record += '"'+ str(riga.riga.delay)+'";'
                    Record += "\r\n"
                import pdb;pdb.set_trace()
                File += Record
                out = base64.encodestring(File)   
                           
                return self.write(cr, uid, ids, {'state':'get', 'data':out}, context=context)
            else:
                return {'type': 'ir.actions.act_window_close'}
    
crea_csv_ordinato()
stock_move()


