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
                'totvalore':fileds.float('Totale Valore',digits=(12, 2))
                }
    
    def mappa_categoria(cr,uid,categoria,context):
       nome_cat =''
       continua = True
       while continua:
           if categoria.parent_id:
               categoria = parent_id
           else:
                nome_cat = categoria.name
                continua=False
        
       return nome_cat
   
    def carica_fatturato(self,cr,uid,parametri,context):       
        ok = self._pulisci(cr, uid, context)
        testa = self.pool.get('fiscaldoc.header')
        filtro_data = [('data_documento','<=', parametri.dadata),('data_documento','>=', parametri.dadata)]
        # 2° filtro per causale controlla che la causale doc sia di VENDITA ('C')
        #filtro_caus = [('fiscaldoc_causalidoc.tipo_operazione' ,=, 'C')]
        testate_ids = testa.search(cr, uid, filtro_data)
        if testate_ids:
            for rec_testa in testa.browse(cr, uid, [testate_ids]):
                if rec_testa.tipo_doc.tipo_operazione=='C':
                    # abbiamo un documento che ci interessa
                    for riga_doc in rec_testa.righe_articoli:
                        # scorre i record del documento
                        cerca = ['product_id','=',riga_doc.product_id.id]
                        id_temp = self.search(cr,uid,cerca)
                        if id_temp:
                            # già esistente
                            riga_temp = self.browse(cr,uid,id_temp)[0]
                            rigawr ={
                                     'totqty':riga_temp.totqty+riga_doc.product_uom_qty,
                                     'totvalore':riga_temp.totvalore+riga_doc.totale_riga
                                     }
                            ok = self.write(cr,uid,id_temp,rigawr)
                        else:
                            #nuovo record
                            pass
                            categoria  = riga_doc.product_id.product_tmpl_id.categ_id 
                            cat_name = self.mappa_categoria(cr, uid, categoria, context)
                            rigawr ={
                                     'categoria':cat_name,
                                     'product_id':riga_doc.product_id.id,
                                     'totqty':riga_doc.product_uom_qty,
                                     'totvalore':riga_doc.totale_riga
                                     }
                            id_temp = self.create(cr,uid,rigawr)
        
        
        return


    def carica_prodotto(self,cr,uid,parametri,context):
        ok = self._pulisci(cr, uid, context)
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
                'tipo_Stampa':fields.selection('Tipo Stampa',(('fatturato','Fatturato'),('prodotto','Prodotto'))),
               }
    #_order = ''
    
    
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        if data['form']['tipodoc']==0 or data['form']['tipodoc']==False:
            data['form']['tipodoc']=1
            data['form']['atipodoc']=99999
        result = {'dadata':data['form']['dadata'],'adata':data['form']['adata'],
            
                  'tipodoc':data['form']['tipodoc'],'atipodoc':data['form']['atipodoc'],
                  
                    }
        return result
    
 
    
    def crea_temp(self, cr, uid, ids, data, context=None):
        parametri = self.browse(cr,uid,ids)[0]
        righe = self.pool.get('fiscaldoc.righe')
        testa = self.pool.get('fiscaldoc.header')
        if parametri.tipo_Stampa == 'fatturato':
            ok = self.pool.get ('tempstatistiche.art').carica_fatturato(cr,uid,parametri,context)
        else:
            ok = self.pool.get ('tempstatistiche.art').carica_prodotto(cr,uid,parametri,context)
        
                
                
                
        
        
    
            
                
            
        
    
    
parcalcolo_fatturato()   