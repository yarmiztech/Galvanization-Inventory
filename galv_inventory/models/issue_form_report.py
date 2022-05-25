from odoo import models, fields, api

class InventoryCategory(models.Model):
   _name = 'inventory.category'

   name = fields.Char(string="Category")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    inventory_categ = fields.Many2one('inventory.category')


class ProductReport(models.Model):
    _name = 'product.report'

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')

    total = fields.Float('Total', compute='compute_total')

    pr_conn = fields.One2many('product.report.line', 'pr_conn1')

    @api.depends('pr_conn')
    def compute_total(self):
        for each in self:
            each.total = sum(each.pr_conn.mapped('amount'))

    @api.onchange('from_date', 'to_date')
    def onchange_date(self):
        if self.from_date and self.to_date:
            datas = self.env['issue.form'].search([('issue_date', '>=', self.from_date), ('issue_date', '<=', self.to_date)])
            data_list = []
            for data in datas:
                for line in data.connection:
                    values = (0, 0, {
                        'issued_to': data.issued_to.name,
                        'product': line.product.id,
                        'category': line.product.categ_id.id,
                        'category_inventory': line.product.inventory_categ.id,
                        'quantity': line.quantity,
                        'unit': line.unit.name,
                        'amount': line.amount,
                    })
                    data_list.append(values)
            self.pr_conn = None
            self.pr_conn = data_list


class ProductReportLine(models.Model):
    _name = 'product.report.line'

    issued_to = fields.Char('Issued To')
    product = fields.Many2one('product.product', string='Product')
    category = fields.Many2one('product.category')
    category_inventory = fields.Many2one('inventory.category')
    quantity = fields.Float('Quantity')
    unit = fields.Char('Unit')
    amount = fields.Float('Amount')
    pr_conn1 = fields.Many2one('product.report')

