# -*- encoding: utf-8 -*-

import wizard
import decimal_precision as dp
import pooler
import time
from tools.translate import _
from osv import osv, fields
from tools.translate import _

class tempstatistiche_art(osv.osv):
    
    def _pulisci(self,cr,uid,context):
        ids = self.search(cr,uid,[])
        ok = self.unlink(cr,uid,ids,context)
        return True

    _name = 'tempstatistiche.art'
    _description = 'Temporaneo Stampa del Fatturato'
    _columns = {
                'categoria':fields.char('categoria',size=64),
                'product_id': fields.many2one('product.product', 'Articolo', required=True),
                'totqty':fields.float('Totale Qta',digits=(12, 2)),
                'totvalore':fields.float('Totale Valore',digits=(12, 2)),
                'pesoconai':fields.float('Peso Conai', digits=(12,2))
                }
    
    def mappa_categoria(self, cr,uid,categoria,context):
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
   
    def carica_fatturato(self,cr,uid,parametri,context):
          
        ok = self._pulisci(cr, uid, context)
        testa = self.pool.get('fiscaldoc.header')
        partner_obj = self.pool.get('res.partner')
        if parametri.agente:
            filtro_ag =[('agent_id','=',parametri.agente.id)]
            partner_ids = partner_obj.search(cr, uid, filtro_ag)
            partner_ids = tuple(partner_ids)
            filtro_data = [('data_documento','<=', parametri.adata),('data_documento','>=', parametri.dadata), ('partner_id', 'in', partner_ids)]
        else:       
            filtro_data = [('data_documento','<=', parametri.adata),('data_documento','>=', parametri.dadata)]
        # 2° filtro per causale controlla che la causale doc sia di VENDITA ('C')
        #filtro_caus = [('fiscaldoc_causalidoc.tipo_operazione' ,=, 'C')]
        testate_ids = testa.search(cr, uid, filtro_data)
       
        if testate_ids:
            for rec_testa in testa.browse(cr, uid, testate_ids):
                if rec_testa.tipo_doc.tipo_operazione=='C':
                    # abbiamo un documento che ci interessa
                    
                    
                        for riga_doc in rec_testa.righe_articoli:
                            #import pdb;pdb.set_trace() 
                            #CONTROLLO CHE IL DDT NON SI STATO GIA' FATTURATO
                            if not rec_testa.differita_id:
                                # scorre i record del documento
                               
                                cerca = [('product_id','=',riga_doc.product_id.id)]
                                id_temp = self.search(cr,uid,cerca)
                                if id_temp:
                            # già esistente
                                    riga_temp = self.browse(cr,uid,id_temp)[0]
                                    if rec_testa.tipo_doc.tipo_documento == 'NC':
                                        rigawr ={
                                                 'totqty':riga_temp.totqty-riga_doc.product_uom_qty,
                                                 'totvalore':riga_temp.totvalore-riga_doc.totale_riga
                                             
                                                 }
                                        ok = self.write(cr,uid,id_temp,rigawr)
                                    
                                    
                                    else:
                                        rigawr ={
                                                 'totqty':riga_temp.totqty+riga_doc.product_uom_qty,
                                                 'totvalore':riga_temp.totvalore+riga_doc.totale_riga
                                             
                                                 }
                                        ok = self.write(cr,uid,id_temp,rigawr)
                                else:
                            #nuovo record
                            #pass
                                    categoria  = riga_doc.product_id.product_tmpl_id.categ_id 
                                    cat_name = self.mappa_categoria(cr, uid, categoria, context)
                                    if rec_testa.tipo_doc.tipo_documento == 'NC':
                                        rigawr ={
                                             'categoria':cat_name,
                                             'product_id':riga_doc.product_id.id,
                                             'totqty':riga_doc.product_uom_qty*-1,
                                             'totvalore':riga_doc.totale_riga*-1
                                                }
                                        id_temp = self.create(cr,uid,rigawr)
                                    else:
                                        rigawr ={
                                             'categoria':cat_name,
                                             'product_id':riga_doc.product_id.id,
                                             'totqty':riga_doc.product_uom_qty,
                                             'totvalore':riga_doc.totale_riga
                                                }
                                        id_temp = self.create(cr,uid,rigawr)
                            else:
                                pass
                            
        
        
        return
    
    def carica_categorie(self,cr,uid,parametri,context):
          
        ok = self._pulisci(cr, uid, context)
        testa = self.pool.get('fiscaldoc.header')
        filtro_data = [('data_documento','<=', parametri.adata),('data_documento','>=', parametri.dadata)]
        # 2° filtro per causale controlla che la causale doc sia di VENDITA ('C')
        #filtro_caus = [('fiscaldoc_causalidoc.tipo_operazione' ,=, 'C')]
        testate_ids = testa.search(cr, uid, filtro_data)
        categ = parametri.categoria.child_id
        # 
        lista_id=[]
        lista_id.append(parametri.categoria.id)
        for riga in categ:
            lista_id.append(riga.id)
           
            #import pdb;pdb.set_trace()
            if riga.child_id:
                sottocateg=riga.child_id
                for new in sottocateg:
                    lista_id.append(new.id)
            
                
            
        if testate_ids:
            for rec_testa in testa.browse(cr, uid, testate_ids):
                if rec_testa.tipo_doc.tipo_operazione=='C':
                    # abbiamo un documento che ci interessa
                    
                    
                        for riga_doc in rec_testa.righe_articoli:
                            #
                            #CONTROLLO CHE IL DDT NON SI STATO GIA' FATTURATO
                            if not rec_testa.differita_id:
                                 
                                 if riga_doc.product_id.product_tmpl_id.categ_id.id in lista_id:
                                     # scorre i record del documento
                                     cerca = [('product_id','=',riga_doc.product_id.id)]
                                     id_temp = self.search(cr,uid,cerca)
                                     if id_temp:
                                            # già esistente
                                            riga_temp = self.browse(cr,uid,id_temp)[0]
                                            if rec_testa.tipo_doc.tipo_documento == 'NC':
                                                rigawr ={
                                                 'totqty':riga_temp.totqty-riga_doc.product_uom_qty,
                                                  'totvalore':riga_temp.totvalore-riga_doc.totale_riga,
                                                  'pesoconai':riga_temp.pesoconai-riga_doc.peso_conai
                                             
                                                 }
                                                ok = self.write(cr,uid,id_temp,rigawr)
                                    
                                    
                                            else:
                                                rigawr ={
                                                 'totqty':riga_temp.totqty+riga_doc.product_uom_qty,
                                                  'totvalore':riga_temp.totvalore+riga_doc.totale_riga,
                                                  'pesoconai':riga_temp.pesoconai+riga_doc.peso_conai
                                             
                                                 }
                                                ok = self.write(cr,uid,id_temp,rigawr)
                                     else:
                                        #nuovo record
                                        #pass
                                        
                                        cat_name = riga_doc.product_id.product_tmpl_id.categ_id.name
                                        if rec_testa.tipo_doc.tipo_documento == 'NC':
                                            rigawr ={
                                                 'categoria':cat_name,
                                                 'product_id':riga_doc.product_id.id,
                                                 'totqty':riga_doc.product_uom_qty*-1,
                                                 'totvalore':riga_doc.totale_riga*-1,
                                                 'pesoconai':riga_doc.peso_conai*-1
                                                 }
                                            id_temp = self.create(cr,uid,rigawr)
                                        else:
                                        
                                                 rigawr ={
                                                          'categoria':cat_name,
                                                          'product_id':riga_doc.product_id.id,
                                                          'totqty':riga_doc.product_uom_qty,
                                                          'totvalore':riga_doc.totale_riga,
                                                          'pesoconai':riga_doc.peso_conai
                                                          }
                                                 id_temp = self.create(cr,uid,rigawr)
                            else:
                                pass
                            
        
        
        return
    
    def carica_categorie_prod(self,cr,uid,parametri,context):
          
        ok = self._pulisci(cr, uid, context)
        mrp = self.pool.get('mrp.production')
        filtro_data = [('date_start','<=', parametri.adata),('date_start','>=', parametri.dadata)]
        mrp_ids = mrp.search(cr, uid, filtro_data)
        #testate_ids = testa.search(cr, uid, filtro_data)
        categ = parametri.categoria.child_id
        # 
        lista_id=[]
        lista_id.append(parametri.categoria.id)
        for riga in categ:
            lista_id.append(riga.id)
           
            #import pdb;pdb.set_trace()
            if riga.child_id:
                sottocateg=riga.child_id
                for new in sottocateg:
                    lista_id.append(new.id)
            
                
            
        if mrp_ids:
            for rec_mrp in mrp.browse(cr, uid, mrp_ids):
                if rec_mrp.product_id.product_tmpl_id.categ_id.id in lista_id:
                    cerca = [('product_id','=',rec_mrp.product_id.id)]
                    #import pdb;pdb.set_trace() 
                    if rec_mrp.state == "done":
                        id_temp = self.search(cr,uid,cerca)
                        if id_temp:
                            riga_temp = self.browse(cr,uid,id_temp)[0]
                    
                            rigawr ={
                                          'totqty':riga_temp.totqty+rec_mrp.product_qty,
                                          'totvalore':riga_temp.totvalore+rec_mrp.total_production_cost
                                          }
                            ok = self.write(cr,uid,id_temp,rigawr)
                        else:
                            #nuovo record
                            #pass
                            cat_name  = rec_mrp.product_id.product_tmpl_id.categ_id.name
                            #cat_name = self.mappa_categoria(cr, uid, categoria, context)
                            rigawr ={'categoria':cat_name,
                                     'product_id':rec_mrp.product_id.id,
                                     'totqty':rec_mrp.product_qty,
                                     'totvalore':rec_mrp.total_production_cost
                                     }
                            id_temp = self.create(cr,uid,rigawr)     
        
        return


    def carica_prodotto(self,cr,uid,parametri,context):
        ok = self._pulisci(cr, uid, context)
        mrp = self.pool.get('mrp.production')
        filtro_data = [('date_start','<=', parametri.adata),('date_start','>=', parametri.dadata)]
        mrp_ids = mrp.search(cr, uid, filtro_data)
        if mrp_ids:
            for rec_mrp in mrp.browse(cr, uid, mrp_ids):
                #for riga_mrp in rec_mrp
                cerca = [('product_id','=',rec_mrp.product_id.id)]
                #import pdb;pdb.set_trace() 
                if rec_mrp.state == "done":
                    id_temp = self.search(cr,uid,cerca)
                    if id_temp:
                        riga_temp = self.browse(cr,uid,id_temp)[0]
                    
                        rigawr ={
                                 'totqty':riga_temp.totqty+rec_mrp.product_qty,
                                 'totvalore':riga_temp.totvalore+rec_mrp.total_production_cost
                                 }
                        ok = self.write(cr,uid,id_temp,rigawr)
                    else:
                            #nuovo record
                            #pass
                            categoria  = rec_mrp.product_id.product_tmpl_id.categ_id 
                            cat_name = self.mappa_categoria(cr, uid, categoria, context)
                            rigawr ={'categoria':cat_name,
                                     'product_id':rec_mrp.product_id.id,
                                     'totqty':rec_mrp.product_qty,
                                     'totvalore':rec_mrp.total_production_cost
                                     }
                            id_temp = self.create(cr,uid,rigawr)
                else:
                    pass
        return

 
    

tempstatistiche_art()

class parcalcolo_fatturato(osv.osv_memory):
    _name = 'parcalcolo.fatturato'
    _description = 'Stampa del Fatturato per categoria ed articolo'
    _columns = {
                # CAMPI CHE SERVONO PER LA SCRITTURA DELLA RIGA
                # nome articolo(fiscaldoc.righe_descrizione_riga)
                # quantità_totale venduta (calcolato, somma righe uguali)
                # prezzo di vendita (calcolata, somma totale di riga)
                # 
                'dadata': fields.date('Da Data Documento', required=True  ),
                'adata': fields.date('A Data Documento', required=True),
                'tipodoc':fields.many2one('fiscaldoc.causalidoc', 'Da tipo documento'),
                'atipodoc':fields.many2one('fiscaldoc.causalidoc', 'A tipo documento'),
                'categoria':fields.many2one('product.category', 'Categoria') ,
                'tipo_Stampa':fields.selection([('FATTURATO','Fatturato'),('PRODOTTO','Prodotto')],'Tipo Stampa', required=True),
                'agente':fields.many2one('sale.agent', 'Agente'),
               }
    #_order = ''
    
    
    def _build_contexts(self, cr, uid, ids, data, parametri, context=None):
        if context is None:
            context = {}
        result = {}
        val = ' '
        val2= ' '
        #if data['form']['tipodoc']==0 or data['form']['tipodoc']==False:
        #     data['form']['tipodoc']=1
        #     data['form']['atipodoc']=99999
        #import pdb;pdb.set_trace()
        #CONVERTE LA DATA IN FORMATO GG/MM/AAAA
        parametri.dadata = time.strptime(parametri.dadata, "%Y-%m-%d")
        parametri.dadata=time.strftime("%d/%m/%Y",parametri.dadata)
        
        parametri.adata = time.strptime(parametri.adata, "%Y-%m-%d")
        parametri.adata=time.strftime("%d/%m/%Y",parametri.adata)
        if parametri.categoria:
            val = parametri.categoria.name
        if parametri.agente:
            val2 = parametri.agente.name
        result = {'dadata':parametri.dadata,'adata':parametri.adata, 
                  'tipo_Stampa':parametri.tipo_Stampa, 'categoria':val, 'agente':val2

                  #'tipodoc':data['form']['tipodoc'],'atipodoc':data['form']['atipodoc'],
                  
                    }
        #import pdb;pdb.set_trace()
        return result
     
    def _print_report(self, cr, uid, ids, data, parametri, context=None):
       
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['dadata',  'adata','tipo_Stampa','categoria'])[0] #  'tipodoc', 'atipodoc' 
        used_context = self._build_contexts(cr, uid, ids, data, parametri, context=context)
        data['form']['parameters'] = used_context
        pool = pooler.get_pool(cr.dbname)
        #fatture = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])
        Primo = True
        if data['form']['categoria']:
            return{'type': 'ir.actions.report.xml',
                   'report_name': 'categorie',
                   #'report_name': 'fatturato',
                   'datas': data,
                   }
        else:
            return {'type': 'ir.actions.report.xml',
                'report_name': 'fatturato',
                'datas': data,
                }
    
 
    
    def crea_temp(self, cr, uid, ids, data, context=None):
        #import pdb;pdb.set_trace()
        parametri = self.browse(cr,uid,ids)[0]
        righe = self.pool.get('fiscaldoc.righe')
        testa = self.pool.get('fiscaldoc.header')
        if parametri.tipo_Stampa == 'FATTURATO':
                if parametri.categoria:
                    ok = self.pool.get('tempstatistiche.art').carica_categorie(cr,uid,parametri,context)
                else:
                    ok = self.pool.get('tempstatistiche.art').carica_fatturato(cr,uid,parametri,context)
        else:
            if parametri.categoria:
                ok = self.pool.get('tempstatistiche.art').carica_categorie_prod(cr,uid,parametri,context)
            else:
                ok = self.pool.get('tempstatistiche.art').carica_prodotto(cr,uid,parametri,context)
        
        
       
        return self._print_report(cr, uid, ids, data, parametri, context=context)
    
   
    
        
                
                
                
        
        
    
            
                
            
        
    
    
parcalcolo_fatturato()   
