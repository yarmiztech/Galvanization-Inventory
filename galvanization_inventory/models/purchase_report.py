from odoo import fields, models, api

class ProductReports(models.Model):
    _name = 'product.reports'

    from_date = fields.Datetime('From Date')
    to_date = fields.Datetime('To Date')

    connection = fields.One2many('product.reports.lines', 'conn')

    @api.onchange('from_date', 'to_date')
    def onchange_date(self):
        if self.from_date and self.to_date:
            datas = self.env['stock.picking'].search([
                ('scheduled_date', '>=', self.from_date),
                ('scheduled_date', '<=', self.to_date)
            ])
            data_list = []
            for data in datas:
                for i in data.purchase_id.order_line:
                    for line in data.move_ids_without_package:
                        if i.product_id.name == line.product_id.name:
                            values = (0, 0, {
                                'date': data.scheduled_date,
                                'grn_no': data.purchase_id.grn_no,
                                'product_code': line.product_id.default_code,
                                'product': line.product_id.id,
                                'category': line.product_id.categ_id,
                                'uom': i.product_uom.id,
                                'quantity': line.product_uom_qty,
                                'rate': line.price_unit,
                                'total': i.price_subtotal,
                            })
                            data_list.append(values)
            self.connection = None
            self.connection = data_list

class ProductsReportsLines(models.Model):
    _name = 'product.reports.lines'

    conn = fields.Many2one('product.reports')

    date = fields.Datetime('Date')
    grn_no = fields.Char('GRN No')
    product_code = fields.Char('Product Code')
    product = fields.Many2one('product.product', 'Product')
    category = fields.Many2one('product.category', 'Category')
    uom = fields.Many2one('uom.uom', 'UOM')
    quantity = fields.Float('Quantity')
    rate = fields.Float('Unit Price')
    total = fields.Float('Total')
