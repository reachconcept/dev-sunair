from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CrmApplication(models.Model):
    _name = 'crm.application'
    _description = 'Dealer Application'
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

    lead_id = fields.Many2one('crm.lead', string='Lead', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    territory_id = fields.Many2one('crm.territory', string='Territory', tracking=True)
    user_id = fields.Many2one('res.users', string='Salesperson', tracking=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    order_id = fields.Many2one('sale.order', string='Sales Order', readonly=True)

    document_count = fields.Integer(compute='_compute_document_count')

    company_legal_name = fields.Char(string='Company Legal Name', tracking=True)
    dba_name = fields.Char(string='Trading As / DBA Name(s)', tracking=True)
    street = fields.Char(string='Street Address')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id.code', '=', 'US')]")
    zip_code = fields.Char(string='ZIP')
    phone = fields.Char(string='Phone')
    fax = fields.Char(string='FAX')
    cell = fields.Char(string='Cell')
    billing_street = fields.Char(string='Billing Street Address')
    billing_city = fields.Char(string='Billing City')
    billing_state_id = fields.Many2one('res.country.state', string='Billing State', domain="[('country_id.code', '=', 'US')]")
    billing_zip = fields.Char(string='Billing ZIP')
    email = fields.Char(string='Email Address')

    business_type = fields.Selection([
        ('sole_proprietorship', 'Sole Proprietorship'),
        ('partnership', 'Partnership'),
        ('corporation', 'Corporation'),
        ('llc', 'LLC'),
        ('s_corp', 'S Corp'),
        ('other', 'Other')
    ], string='Type of Business')
    business_type_other = fields.Char(string='Other Business Type')
    duns_number = fields.Char(string='DUN & Bradstreet ID #')
    year_established = fields.Char(string='Year Business Established')
    federal_id = fields.Char(string='Federal Identification #')

    tax_status = fields.Selection([
        ('taxable', 'Taxable'),
        ('tax_exempt', 'Tax Exempt')
    ], string='Tax Status', default='taxable')
    tax_exempt_number = fields.Char(string='Tax Exempt #')
    multi_jurisdiction_attached = fields.Boolean(string='Multi Jurisdiction Form Attached')

    principle_name_1 = fields.Char(string='Name')
    principle_title_1 = fields.Char(string='Title')
    principle_ssn_1 = fields.Char(string='SSN')
    principle_address_1 = fields.Char(string='Address')
    principle_city_1 = fields.Char(string='City')
    principle_state_id_1 = fields.Many2one('res.country.state', string='State', domain="[('country_id.code', '=', 'US')]")
    principle_phone_1 = fields.Char(string='Phone')

    principle_name_2 = fields.Char(string='Name')
    principle_title_2 = fields.Char(string='Title')
    principle_ssn_2 = fields.Char(string='SSN')
    principle_address_2 = fields.Char(string='Address')
    principle_city_2 = fields.Char(string='City')
    principle_state_id_2 = fields.Many2one('res.country.state', string='State', domain="[('country_id.code', '=', 'US')]")
    principle_phone_2 = fields.Char(string='Phone')

    bank_name = fields.Char(string='Name of Bank')
    bank_account_number = fields.Char(string='Account #')
    bank_address = fields.Char(string='Address')
    bank_city = fields.Char(string='City')
    bank_state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id.code', '=', 'US')]")
    bank_zip = fields.Char(string='ZIP')

    trade_ref_1_name = fields.Char(string='Name')
    trade_ref_1_phone = fields.Char(string='Phone')
    trade_ref_1_fax = fields.Char(string='FAX')
    trade_ref_1_address = fields.Char(string='Address')

    trade_ref_2_name = fields.Char(string='Name')
    trade_ref_2_phone = fields.Char(string='Phone')
    trade_ref_2_fax = fields.Char(string='FAX')
    trade_ref_2_address = fields.Char(string='Address')

    trade_ref_3_name = fields.Char(string='Name')
    trade_ref_3_phone = fields.Char(string='Phone')
    trade_ref_3_fax = fields.Char(string='FAX')
    trade_ref_3_address = fields.Char(string='Address')

    other_business_names = fields.Text(string='Other Business Names')
    has_other_business_names = fields.Boolean(string='Doing business under other names?')
    has_bankruptcy = fields.Boolean(string='Has any principle been involved in bankruptcy?')
    bankruptcy_dates = fields.Char(string='Bankruptcy Date(s)')

    signed_by_name = fields.Char(string='Signer Name')
    signed_by_title = fields.Char(string='Title')
    signature_date = fields.Date(string='Date')
    dealer_representative = fields.Char(string='Dealer Representative')

    is_awcbn = fields.Boolean(string='AWCBN Member')
    awcbn_number = fields.Char(string='AWCBN Number')

    def action_send_application(self):
        self.state = 'sent'

    def action_send_to_finance(self):
        for rec in self:
            if rec.document_count == 0:
                raise ValidationError("Please attach the Dealer Application documents received.")
            if not rec.signed_by_name or not rec.signature_date:
                raise ValidationError("Please ensure the application is signed and dated.")
            rec.state = 'ar_approval'

    def action_ar_approve(self):
        self.state = 'manager_approval'

    def action_manager_approve(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_id.write({
                    'is_company': True,
                    'street': rec.street,
                    'city': rec.city,
                    'state_id': rec.state_id.id,
                    'zip': rec.zip_code,
                    'phone': rec.phone,
                    'email': rec.email,
                })
                rec.partner_id.is_dealer = True

            products = self.env['product.product'].search([
                ('is_dealer_starter_kit', '=', True)
            ])

            if products and rec.partner_id:
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
            'domain': [('res_model', '=', 'crm.application'), ('res_id', '=', self.id)],
            'context': {'default_res_model': 'crm.application', 'default_res_id': self.id}
        }

    def action_view_order(self):
        if self.order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Sales Order',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'res_id': self.order_id.id,
                'target': 'current',
            }

    def action_create_partner(self):
        if not self.partner_id:
            partner = self.env['res.partner'].create({
                'name': self.company_legal_name,
                'is_company': True,
                'street': self.street,
                'city': self.city,
                'state_id': self.state_id.id,
                'zip': self.zip_code,
                'phone': self.phone,
                'email': self.email,
                'is_dealer': True,
            })
            self.partner_id = partner.id
        return self.partner_id

    @api.depends()
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'crm.application'),
                ('res_id', '=', rec.id)
            ])

    @api.constrains('year_established')
    def _check_year_established(self):
        for rec in self:
            if rec.year_established and (not rec.year_established.isdigit() or int(rec.year_established) < 1900 or int(rec.year_established) > 2026):
                raise ValidationError("Please enter a valid year.")

    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email and '@' not in rec.email:
                raise ValidationError("Please enter a valid email address.")

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('crm.application') or 'New'
        return super().create(vals_list)