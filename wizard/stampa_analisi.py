# -*- encoding: utf-8 -*-

import wizard
import decimal_precision as dp
import pooler
import time
from tools.translate import _
from osv import osv, fields
from tools.translate import _
from datetime import datetime, timedelta
import base64
from tempfile import TemporaryFile
import math

import tools
import ir


#from tools.translate import _
import csv
import sys
import os
import re

class tempstatistiche_analisi(osv.osv):
    _name = 'tempstatistiche.analisi'
    _description = 'temporaneo per la stampa delle analisi del venduto'
    _columns = {'analisi_id': fields.many2one('analisi.venduto', 'ID_Analisi'),
                'valore1': fields.float('Totale1', digits=(25,2)),
                'valore2': fields.float('Totale2', digits=(25,2)),
                'valore3': fields.float('Totale3', digits=(25,2)),
                'range1': fields.char('Range1', size=20),
                'range2': fields.char('Range2', size=20),
                'range3': fields.char('Range3', size=20),
                'partner':fields.char('Cliente', size=20),
                'agente':fields.char('Agente', size=20),
                
                }
    

    def carica_doc(cr,uid,parametri,context):
        periodi_obj = self.pool.get('account.period')
        analisi_obj = self.pool.get('analisi.venduto')
        agente_obj = self.pool.get('sale.agent')
        partner_obj = self.pool.get('res.partner')
        v = {}
        import pdb;pdb.set_trace()
        if parametri.periodo1:
            filtro = [('periodo_id','=',parametri.periodo1)]
        elif parametri.periodo1 and parametri.partner:
            filtro = [('name', '=', parametri.partner), ('periodo_id','=',parametri.periodo1)]
        else:
            partner_ids = partner_obj.search(cr, uid, parametri.partner)
            filtro =[('periodo_id','=',parametri.periodo1), ('name','in',partner_ids)]
                
        idriga1 = analisi_obj.search(cr, uid, filtro) 
        if idriga1:  
            riga = analisi_obj.browse(cr, uid,idriga1[0])
            riga={'anlisi_id':idriga1[0],
                  'range1':riga.periodo_id.name,
                  'valore1':riga.totale,
                  'partner':parametri.partner,
                  'agente':parametri.agente,
                     }
        if parametri.periodo2:
            filtro2 = [('periodo_id','=',parametri.periodo2)]
        elif parametri.periodo2 and parametri.partner:
            filtro2 = [('name', '=', parametri.partner), ('periodo_id','=',parametri.periodo2)]
        else:
            #partner_ids = partner_obj.search(cr, uid, parametri.agente)
            filtro2 =[('periodo_id','=',parametri.periodo2), ('name','in',partner_ids)]
        idriga2 = analisi_obj.search(cr, uid, filtro2) 
        if idriga2:
            riga = analisi_obj.browse(cr, uid,idriga2[0])
            riga={'range2':riga.period_id.name,
                  'valore2':riga.totale,
                  }
        if parametri.periodo3:
            filtro3 = [('periodo_id','=',parametri.periodo3)]
        elif parametri.periodo3 and parametri.partner:
            filtro3 = [('name', '=', parametri.partner), ('periodo_id','=',parametri.periodo3)]
        else:
            #partner_ids = partner_obj.search(cr, uid, parametri.agente)
            filtro3 =[('periodo_id','=',parametri.periodo3), ('name','in',partner_ids)]
        idriga3 = analisi_obj.search(cr, uid, filtro3)
        if idriga3:
            riga = analisi_obj.browse(cr, uid,idriga3[0])
            riga={'range3':riga.period_id.name,
                  'valore3':riga.totale,
                  }
        ok = self.create(cr,uid,riga)
        return True
        
            
            
                
        
        

tempstatistiche_analisi()

class stampa_analisi_venduto (osv.osv_memory):
    _name = 'stampa.analisi.venduto'
    _description = 'parametri di stampa jasper per le analisi del venduto'
    _columns = {'periodo1': fields.many2one('account.period', 'Periodo anno n', required=True),
                
                'periodo2': fields.many2one('account.period', 'Periodo anno n-1', required=True),
                
                'periodo3': fields.many2one('account.period', 'Periodo anno n-2', required=True),
                
                'partner':fields.many2one('res.partner', 'Cliente'),
                'agente':fields.many2one('sale.agent', 'Agente'),
                }
    
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        parametri = self.browse(cr,uid,ids)[0]
        if parametri.agente:
            data['form']['agente']=parametri.agente.id
        else:
             data['form']['agente']= 0
        #import pdb;pdb.set_trace()
        result = { 'periodo1':data['form']['periodo1'],'periodo2':data['form']['periodo2'],
                   'periodo3':data['form']['periodo3'], 
                  'partner':data['form']['partner'], 'agente':data['form']['agente']}
        
    def _print_report(self, cr, uid, ids, data, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
        pool = pooler.get_pool(cr.dbname)
        #fatture = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])
        Primo = True
        return {
                            'type': 'ir.actions.report.xml',
                            'report_name': 'venduto',
                            'datas': data,
                            }
    def check_report(self, cr, uid, ids, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
            
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['dadata1_1', 'dadata1_2', 'dadata2_1', 'dadata2_2', 'dadata3_1', 'dadata3_2', 'partner', 'agente'])[0]
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
    
    def crea_temp(self,cr, uid, ids, data, context=None):
        parametri = self.browse(cr,uid,ids)[0]
        ok = self.pool.get('tempstatistiche.analisi').carica_doc(cr,uid,parametri,context)
    
    def on_change_value(self, cr, uid, ids, periodo1, context):
        
        v = {}
        periodi_obj = self.pool.get('account.period')
        periodo = periodi_obj.browse(cr, uid, periodo1)
        dt = periodo.date_start
        data_1 = datetime.strptime(dt, '%Y-%m-%d')
        anno = data_1.year
        anno = anno - 1
        giorno = data_1.day
        mese = data_1.month
        giornos = str(giorno).zfill(2)
        meses = str(mese).zfill(2)
        annos = str(anno)
        nuova_data = annos + "-" + meses + "-" + giornos
        filtro = [('date_start', '=', nuova_data)]
        nuovo_id = periodi_obj.search(cr, uid, filtro)
        #import pdb;pdb.set_trace()

        if nuovo_id:
            v['periodo2']=nuovo_id[0]
            anno = anno - 1
            annos = str(anno)
            nuova_data = annos + "-" + meses + "-" + giornos
            filtro = [('date_start', '=', nuova_data)]
            secondo_id = periodi_obj.search(cr, uid, filtro)
            if secondo_id:
                
                v['periodo3']=secondo_id[0]
        return {'value': v}
                    
stampa_analisi_venduto()