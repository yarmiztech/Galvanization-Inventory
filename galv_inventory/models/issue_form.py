from odoo import models, fields, api,_
from odoo.tests.common import Form


class IssueForm(models.Model):
    _name = 'issue.form'

    name = fields.Char("Name", index=True,default=lambda self: _('New'))
    issued_to = fields.Many2one('hr.employee', string='Issued To')
    address = fields.Char('Address')
    issue_ticket_no = fields.Char('Issue Ticket No')
    phone = fields.Char('Phone')
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Validate'), ('cancelled', 'Cancelled')], default='draft',readonly=True,)
    mobile = fields.Char('Mobile')
    issue_date = fields.Date('Issue Date')
    issue_req = fields.Many2one('employee.requisition')
    net_total = fields.Float('Net Total', compute='compute_net_amount')
    connection = fields.One2many('issue.form.line', 'conn')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'issue.form') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('issue.form') or _('New')
                vals['issue_ticket_no'] = vals['name']
        return super(IssueForm, self).create(vals)

    @api.depends('connection')
    def compute_net_amount(self):
        for each in self:
            each.net_total = sum(each.connection.mapped('amount'))

    def validate(self):
        list = []
        for line in self.connection:
            dict = (0, 0, {
                'name': line.product.display_name,
                'product_id': line.product.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product.uom_id.id,
                'location_id': self.env['stock.location'].search(
                    [('company_id', '=', self.env.user.company_id.id)]
                ).filtered(lambda a: a.display_name == 'WH/Stock').id,
                'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                'picking_type_id': self.env['stock.picking.type'].search([('code', '=', 'outgoing')]).id,

            })
            list.append(dict)
        picking = self.env['stock.picking'].create({
            'partner_id': self.issued_to.address_home_id.id,
            'picking_type_id': self.env['stock.picking.type'].search([('code', '=', 'outgoing')]).id,

            'location_id': self.env['stock.location'].search(
                [('company_id', '=', self.env.user.company_id.id)]
            ).filtered(lambda a: a.display_name == 'WH/Stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            'move_lines': list
        })
        picking.action_assign()
        m = picking.button_validate()
        print(m)
        self.write({'state':'validate'})
        Form(self.env['stock.immediate.transfer'].with_context(m['context'])).save().process()
        self.state = 'validate'

class IssueFormLine(models.Model):
    _name = 'issue.form.line'

    product = fields.Many2one('product.product', string='Product')
    product_code = fields.Char('Product Code')
    unit = fields.Many2one('uom.uom', string='Unit')
    purchase_value = fields.Float('Purchase Value')
    quantity = fields.Float('Quantity')
    amount = fields.Float('Amount', compute='compute_amount')
    remarks = fields.Text('Remarks')
    conn = fields.Many2one('issue.form')

    @api.depends('purchase_value', 'quantity')
    def compute_amount(self):
        for line in self:
            line.amount = line.quantity*line.purchase_value

    @api.onchange('product')
    def _onchange_product(self):
        if self.product:
            self.product_code = self.product.default_code
            self.unit = self.product.uom_id



