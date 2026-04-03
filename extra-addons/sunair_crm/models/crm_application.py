from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CrmApplication(models.Model):
    _name = 'crm.application'
    _description = 'CRM Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Application Sent'),
        ('ar_approval', 'AR Approval'),
        ('manager_approval', 'Manager Approval'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)

    lead_id = fields.Many2one('crm.lead', tracking=True)
    partner_id = fields.Many2one('res.partner', tracking=True)

    is_awcbn = fields.Boolean()
    awcbn_number = fields.Char()

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    order_id = fields.Many2one('sale.order', readonly=True)

    document_count = fields.Integer(compute='_compute_document_count')

    def action_open_sale_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Order',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.order_id.id,
            'target': 'current',
        }

    @api.depends()
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'crm.application'),
                ('res_id', '=', rec.id)
            ])

    def action_send_application(self):
        self.state = 'sent'

    def action_send_to_finance(self):
        for rec in self:
            if rec.document_count == 0:
                raise ValidationError("Please attach the Dealer Application documents received.")
            rec.state = 'ar_approval'

    def action_ar_approve(self):
        self.state = 'manager_approval'

    def action_manager_approve(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_id.is_dealer = True

            products = self.env['product.product'].search([
                ('is_dealer_starter_kit', '=', True)
            ])

            order = self.env['sale.order'].create({
                'partner_id': rec.partner_id.id,
            })

            for product in products:
                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': product.id,
                    'product_uom_qty': 1,
                    'price_unit': product.lst_price,
                })

            rec.order_id = order.id
            rec.state = 'completed'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_view_documents(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [
                ('res_model', '=', 'crm.application'),
                ('res_id', '=', self.id)
            ],
            'context': {
                'default_res_model': 'crm.application',
                'default_res_id': self.id,
            }
        }

    def action_view_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Order',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.order_id.id
        }

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('crm.application') or 'New'
        return super().create(vals_list)