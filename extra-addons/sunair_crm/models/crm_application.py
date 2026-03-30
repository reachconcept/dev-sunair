from odoo import models, fields, api

class CrmApplication(models.Model):
    _name = 'crm.application'
    _description = 'CRM Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    state = fields.Selection([
        ('sent', 'Application Sent'),
        ('ar_approval', 'AR Approval'),
        ('manager_approval', 'Manager Approval'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='sent', tracking=True)
    lead_id = fields.Many2one('crm.lead', tracking=True)
    partner_id = fields.Many2one('res.partner', tracking=True)
    is_awcbn = fields.Boolean()
    awcbn_number = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    order_id = fields.Many2one('sale.order')
    document_count = fields.Integer(compute='_compute_document_count')

    @api.depends()
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'crm.application'),
                ('res_id', '=', rec.id)
            ])

    def action_send_to_finance(self):
        self.state = 'ar_approval'

    def action_ar_approve(self):
        self.state = 'manager_approval'

    def action_manager_approve(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
        })
        self.order_id = sale_order.id
        self.state = 'completed'

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