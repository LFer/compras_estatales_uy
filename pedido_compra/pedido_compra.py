# -*- coding: utf-8 -*-
from osv import osv
from osv import fields
import openerp.addons.decimal_precision as dp

LISTA_ESTADOS = [
    ('nuevo', 'nuevo'),
    ('pendiente_de_aprobacion', 'Pendiente de aprobación'),
    ('aprobado', 'Aprobado'),
    ('rechazado', 'rechazado'),
    ('afectado', 'Afectado'),
    ('proveedores_invitados', 'Proveedores invitados'),
]
class pedido_compras(osv.osv):
    _name="pedido.compras"
    _columns = {
	
        #'nombre': fields.char('Referencia de Pedido', size=32,required=True),  
        'name': fields.char('Referencia de Pedido', size=32,required=True),
        'origin': fields.char('Source Document', size=32),
        'date_start': fields.date('Fecha Pedido'),
        'date_end': fields.date('Deadline Pedido'),	
        'description': fields.text('Description'),
        'user_id': fields.many2one('res.users', 'Responsible'),
        'company_id': fields.many2one('res.company', 'Company'),
		#nuevas lineas 
        #'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse'), 		
		'line_ids' : fields.one2many('pc_pedidos.line','pc_pedido_id','Products to Purchase'),
		#'Status', track_visibility='onchange', required=True),
		
        'state': fields.selection(LISTA_ESTADOS, 'Estado', size=60, readonly=True),
    }
    ############ Senhal ###########
    def action_Aprobado(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'state':'aprobado'},context)
        return True
    ############ Senhal ###########
    def action_Afectado(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'state':'afectado'},context)
        return True
    ############ Senhal ###########
    def action_Proveedores_invitados(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'state':'proveedores_invitados'},context)
        return True
    ############ Senhal ###########
    def action_Recepcion_de_ofertas(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'state':''},context)
        return True
    ############ Senhal ###########
    def action_Pendiente_de_aprobacion(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'state':'pendiente_de_aprobacion'},context)
        return True
    ############ Senhal ###########
    def action_Rechazado(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'state':'rechazado'},context)
        return True
    _defaults = {
        'state': 'nuevo',
    }

class pc_pedidos_line(osv.osv):

    _name = "pc_pedidos.line"
    _description="Lineas de Pedidos Custom"
    _rec_name = 'product_id'

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
		#'product_id': fields.selection('product.product', 'Product' ),
        'product_uom_id': fields.many2one('product.uom', 'Product Unit of Measure'),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        #'product_qty': fields.float('Quantity'),
        'pc_pedido_id' : fields.many2one('pedido.compras','Pedido', ondelete='cascade'),
        'company_id': fields.related('pc_pedido_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
    }
