# copyright 2022 Sodexis
# license OPL-1 (see license file for full copyright and licensing details).

from odoo import models, fields, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _return_stock_move(self):
        for move in self:
            related_moves = move
            if self._context.get('return_related_stock_moves'):
                related_moves = self.env['stock.move'].search(
                    [('sale_line_id', 'in', move.sale_line_id.order_id.order_line.ids)]).filtered(lambda m: not m.to_refund)
            for related_move in related_moves:
                related_move.move_dest_ids.filtered(
                    lambda m: m.state not in ('done', 'cancel'))._do_unreserve()
                # Unreserve the quantities if the move is not in done or cancel state.
            returned = 0
            for return_move in related_moves:
                if return_move.to_refund:
                    raise UserError(
                        _("This is a returned Stock Move."))
                if return_move.quantity_done:
                    returned += 1
                    vals = {
                        'product_id': return_move.product_id.id,
                        'product_uom_qty': return_move.product_qty,
                        'product_uom': return_move.product_id.uom_id.id,
                        'state': 'draft',
                        'date': fields.Datetime.now(),
                        'location_id': return_move.location_dest_id.id,
                        'location_dest_id': return_move.location_id.id,
                        'origin_returned_move_id': return_move.id,
                        'procure_method': 'make_to_stock',
                        # To Recompute SO after Stock move is done.
                        'to_refund': True,
                    }
                    r = return_move.copy(vals)
                    vals = {}
                    move_orig_to_link = return_move.move_dest_ids.mapped(
                        'returned_move_ids')
                    # link to original move
                    move_orig_to_link |= return_move
                    # link to siblings of original move, if any
                    move_orig_to_link |= return_move\
                        .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))\
                        .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))
                    move_dest_to_link = return_move.move_orig_ids.mapped(
                        'returned_move_ids')
                    move_dest_to_link |= return_move.move_orig_ids.mapped('returned_move_ids')\
                        .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))\
                        .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))
                    vals['move_orig_ids'] = [(4, m.id)
                                             for m in move_orig_to_link]
                    vals['move_dest_ids'] = [(4, m.id)
                                             for m in move_dest_to_link]
                    r.write(vals)
                    r._action_confirm()
                    # To Confirm the Stock Move Created.
                    r._action_assign()
                    # To assign move_line_ids to the move created.
                    r._set_quantities_to_reservation()
                    # To update the Qty Done in move_line_ids.
                    # It will not update the Qty if the move has lot_id.
                    r._action_done()

            if not returned:
                raise UserError(
                    _("Please specify at least one non-zero quantity."))
