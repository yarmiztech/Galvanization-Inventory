from datetime import datetime

from odoo import models, fields, api
from odoo.tests import Form


class PurchaseInherit(models.Model):
    _inherit = 'purchase.order'

    grn_no = fields.Char('GRN no')
    invoice_no = fields.Char('Invoice Number')

    def button_confirm(self):
        super(PurchaseInherit, self).button_confirm()
        # receive_prod_id = self.action_view_picking()
        stock_picking = self.env['stock.picking'].search([('purchase_id', '=', self.id)])
        validate = stock_picking.button_validate()
        self.grn_no = stock_picking.name
        Form(self.env['stock.immediate.transfer'].with_context(validate['context'])).save().process()

class PurchaseLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    p_value = fields.Float('P_Value')

    @api.onchange('p_value')
    def _onchange_p_value(self):
        if self.product_qty:
            value = self.p_value/self.product_qty
            self.price_unit = value

