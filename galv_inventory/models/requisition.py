from datetime import datetime

from odoo import fields, models, api, _


class DepartmentRequistion(models.Model):
    _name = 'department.requisition'

    name = fields.Char('Name')


class EmployeeRequistion(models.Model):
    _name = 'employee.requisition'

    date = fields.Date(default=datetime.today(), string='Date')
    employee = fields.Many2one('hr.employee', 'Employee')
    department = fields.Many2one('hr.department', 'Department')
    employee_conn = fields.One2many('employee.requisition.line', 'conn')
    issue_ids = fields.One2many('issue.form', 'issue_req')

    state = fields.Selection([('draft', 'Draft'), ('form_issued', 'Form Issued')], default='draft',readonly=True,)

    @api.onchange('employee')
    def onchange_department(self):
        if self.employee:
            self.department = self.employee.department_id

    def view_issue_form(self):
        contract_obj = self.env['issue.form'].search([('issue_req', '=', self.id)])
        contract_ids = []
        for each in contract_obj:
            contract_ids.append(each.id)
        view_id = self.env.ref('galv_inventory.issue_form').id
        if contract_ids:
            if len(contract_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'issue.form',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Issue Form'),
                    'res_id': contract_ids and contract_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', contract_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'issue.form',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Issue Form'),
                    'res_id': contract_ids
                }

            return value

    def pass_values(self):
        view_id = self.env.ref('galv_inventory.issue_form').id
        value_list = []
        for line in self.employee_conn:
            values = (0, 0, {
                'product': line.product.id,
                'product_code': line.product.default_code,
                'quantity': line.requested_qty,
                'unit': line.uom.id,
                'purchase_value': line.p_value,
            })
            value_list.append(values)

        # context = self._context.copy()
        print(value_list)
        self.state = 'form_issued'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'issue.form',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'context': {
                'default_issued_to': self.employee.id,
                'default_issue_date': self.date,
                'default_phone': self.employee.work_phone,
                'default_mobile': self.employee.mobile_phone,
                'default_issue_req': self.id,
                'default_address': self.employee.address_home_id.street,
                # 'default_connection': (0, 0, {
                #     'product': line.product.id,
                #     'quantity': line.requested_qty,
                # })
                'default_connection': value_list
            },
            'nodestroy': True,
        }


class EmployeeRequisitionLines(models.Model):
    _name = 'employee.requisition.line'

    conn = fields.Many2one('employee.requisition')
    product = fields.Many2one('product.product', string='Product')
    uom = fields.Many2one('uom.uom', string='Unit Of Measure')
    p_value = fields.Float('Purchase Value')
    available_qty = fields.Float('Available Quantity(s)')
    requested_qty = fields.Float('Requested Quantity(s)')

    @api.onchange('product')
    def onchange_product_id(self):
        if self.product:
            self.uom = self.product.uom_id
            self.p_value = self.product.standard_price
            self.available_qty = self.product.qty_available


class ProductReports(models.Model):
    _inherit = 'product.reports'

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
                                'category_inventory': line.product_id.inventory_categ.id,
                            })
                            data_list.append(values)
            self.connection = None
            self.connection = data_list


class ProductsReportsLines(models.Model):
    _inherit = 'product.reports.lines'

    category_inventory = fields.Many2one('inventory.category')
