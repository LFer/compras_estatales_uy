# -*- coding: utf-8 -*-

from osv import osv
from osv import fields
import openerp.addons.decimal_precision as dp
import time

##
#	El orden de los estados en esta lista determina el orden en
#	que se presentan en la vista.
##

class solicitud_recursos(osv.osv):
	
	_name="solicitud.recursos"

	LISTA_ESTADOS_SOLICITUD = [
		('draft', 'Nuevo'),
		('sent_to_approval', 'En Aprobacion'),
		('approved', 'Aprobado'),
		('rejected', 'Rechazado'),
		('closed_total', 'Cerrado Total'),
		('closed_partial', 'Cerrado Parcial'),
		('purchase_request', 'A comprar' ),
	]

	def _get_company_id(self, cr, uid, context=None):
		res = self.pool.get('res.users').read(cr, uid, [uid], ['company_id'], context=context)
		if res and res[0]['company_id']:
			return res[0]['company_id'][0]
		return False

	def _get_user_id(self, cr, uid, context=None):
		"""
		If the user is logged in (i.e. not anonymous), get the user's name to
		pre-fill the partner_name field.
		Same goes for the other _get_user_attr methods.

		@return current user's name if the user isn't "anonymous", None otherwise
		"""
		user_id = self.pool.get('res.users').read(cr, uid, uid, ['id'], context)

		return user_id['id']
		
	def _get_user_name(self, cr, uid, context=None):
		"""
		If the user is logged in (i.e. not anonymous), get the user's name to
		pre-fill the partner_name field.
		Same goes for the other _get_user_attr methods.

		@return current user's name if the user isn't "anonymous", None otherwise
		"""
		user = self.pool.get('res.users').read(cr, uid, uid, ['login'], context)

		if (user['login'] != 'anonymous'):
			return self.pool.get('res.users').name_get(cr, uid, uid, context)[0][1]
		else:
			return None

	_columns = {
		'name': fields.char ( 'Solicitud', size = 32, required = True ), # Nro Solicitud
#		'origin': fields.char ( 'Documento orígen', size = 32 ),
		'date_start': fields.date ( 'Fecha de solicitud' ), # Fecha de solicitud
		'date_end': fields.date ( 'Vencimiento de solicitud' ),	
		'description': fields.text ( 'Descripción' ),
		'user_id': fields.many2one ( 'res.users', 'Solicitante' ), # Solicitante
		'srl_ids_solicitado' : fields.one2many ( 'solicitud.recursos.line', 'sr_solicitud_id', 'Productos solicitados' ),
		'state': fields.selection ( LISTA_ESTADOS_SOLICITUD, 'Estado', size = 20, readonly = True ),
#		'company_id': fields.many2one ( 'res.company', 'Compañía', select = True, readonly = True ), # Compañía
		'company_id': fields.many2one ( 'res.company','Compañía' ),
		'presupuesto': fields.text ( 'Presupuesto', size = 20 ),

		######################## Estados ####################################
	}

	############ Senhal ###########
	def action_Solicitar_Aprobacion(self, cr, uid, ids, context=None):
		self.write(cr,uid,ids,{'state':'sent_to_approval'},context)
		return True

	############ Senhal ###########
	def action_Consultar_Stock(self, cr, uid, ids, context=None):
		self.write(cr,uid,ids,{'state':'approved'},context)
		return True

	############ Senhal ###########
	def action_Rechazado(self, cr, uid, ids, context=None):
		self.write(cr,uid,ids,{'state':'rejected'},context)
		return True

	############ Senhal ###########
	def action_Sr_Cerrada(self, cr, uid, ids, context=None):
		self.write(cr,uid,ids,{'state':'closed_total'},context)
		return True

	############ Senhal ###########
	def action_Cumple_Parcial(self, cr, uid, ids, context=None):
		self.write(cr,uid,ids,{'state':'closed_partial'},context)
		return True

	############ Senhal ###########
	def action_Para_Compras ( self, cr, uid, ids, context = None ):
		self.write ( cr, uid, ids, { 'state' : 'purchase_request' }, context )
		return True

	_defaults = {
		'state' : 'draft',
		'name' : lambda obj, cr, uid, context: obj.pool.get ( 'ir.sequence' ).get ( cr, uid, 'resource.requisition.number' ),
		'company_id': _get_company_id,
		'user_id': _get_user_id,
		'date_start': time.strftime('%Y-%m-%d'),
	}	

class solicitud_recursos_line ( osv.osv ):

	_name = "solicitud.recursos.line"
	_description="Lineas de Pedidos Custom"
	_rec_name = 'product_id'

	LISTA_ESTADOS_LINEA_SOLICITUD = [
		('noe', 'No entregado'),
		('noh', 'No hay'),
		('total', 'Entregado Total'),
		('parcial', 'Entregado Parcial'),
		('acompra', 'Enviado a compra'),
	]

	def _get_uom_id(self, cr, uid, *args):
		cr.execute('select id from product_uom order by id limit 1')
		res = cr.fetchone()
		return res and res[0] or False

	_columns = {
		'product_id': fields.many2one ('product.product', 'Producto' ), # Producto
		'product_uom_id': fields.many2one('product.uom', 'Unidad de medida'),
		'product_requested_qty': fields.float ( 'Cantidad requerida', digits_compute=dp.get_precision('Unidad de medida')),
		'sr_solicitud_id' : fields.many2one('solicitud.recursos','Solicitado', ondelete='cascade'),
		'state': fields.related ( 'sr_solicitud_id', 'state', type = 'char', readonly=True ),
		'precio': fields.float ( 'Precio' ),
		'comentarios': fields.text ( 'Comentarios', size = 30 ),
		'estado': fields.selection ( LISTA_ESTADOS_LINEA_SOLICITUD, 'Estado', size = 20, readonly = True ),
	}

	defaults = {
		'product_uom_id': _get_uom_id,
	}
