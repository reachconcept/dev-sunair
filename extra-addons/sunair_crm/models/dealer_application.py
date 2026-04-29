from odoo import models, fields, api
from odoo.exceptions import ValidationError
import secrets

class DealerApplication(models.Model):
    _name = 'dealer.application'
    _description = 'Dealer Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    stage_id = fields.Many2one(
        'dealer.application.state',
        string='Stage',
        tracking=True,
        ondelete='set null',
        group_expand='_read_group_stage_ids',
    )
    state_type = fields.Selection(
        related='stage_id.state_type',
        string='State Type',
        store=True,
    )

    lead_id = fields.Many2one('crm.lead', string='Lead', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    territory_id = fields.Many2one('crm.territory', string='Territory', tracking=True)
    dealer_representative_id = fields.Many2one('res.users', string='Representative', tracking=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    order_id = fields.Many2one('sale.order', string='Sales Order', readonly=True)
    request_id = fields.Many2one('dealer.request', string='Dealer Request', readonly=True, copy=False)

    document_count = fields.Integer(compute='_compute_document_count')

    # Fields that are kept in sync with dealer.request (application field -> request field)
    _SYNC_TO_REQUEST = {
        'company_legal_name': 'company',
        'street':             'street',
        'city':               'city',
        'state_id':           'country_state_id',
        'zip_code':           'zip',
        'phone':              'work_phone',
        'email':              'email',
        'partner_id':         'partner_id',
        'lead_id':            'lead_id',
    }

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
    dealer_representative = fields.Char(string='Representative')
    is_awcbn = fields.Boolean(string='AWCBN Member')
    awcbn_number = fields.Char(string='AWCBN Number')

    access_token = fields.Char(
        string='Access Token',
        copy=False,
        readonly=True,
        index=True,
    )
    # Partnership / Onboarding fields
    partnership_zip_code = fields.Char(string='Partnership ZIP Code')
    partnership_order_id = fields.Many2one(
        'sale.order',
        string='Partnership Sales Order',
        readonly=True,
    )
    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get('dealer_sync_skip'):
            return res
        sync_vals = {
            req_field: vals[app_field]
            for app_field, req_field in self._SYNC_TO_REQUEST.items()
            if app_field in vals
        }
        if sync_vals:
            for rec in self:
                if rec.request_id:
                    rec.request_id.with_context(dealer_sync_skip=True).write(sync_vals)
        return res

    def action_view_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dealer Request',
            'res_model': 'dealer.request',
            'view_mode': 'form',
            'res_id': self.request_id.id,
            'target': 'current',
        }

    def _get_state(self, state_type):
        return self.env['dealer.application.state'].search(
            [('state_type', '=', state_type)], limit=1
        )

    @api.model
    def _read_group_stage_ids(self, states, _domain):
        return states.search([])

    def action_send_application(self):
        template = self.env.ref('sunair_crm.dealer_application_invite_email')

        for rec in self:
            if not rec.partner_id or not rec.partner_id.email:
                raise ValidationError("Customer email is missing.")

            template.with_context(mail_notify_author=False).send_mail(rec.id, force_send=True)
            state = self._get_state('sent')
            if state:
                rec.stage_id = state


    def action_send_to_finance(self):
        state = self._get_state('ar_approval')
        for rec in self:
            if rec.document_count == 0:
                raise ValidationError("Please attach the Dealer Application documents received.")
            if not rec.signed_by_name or not rec.signature_date:
                raise ValidationError("Please ensure the application is signed and dated.")
            if state:
                rec.stage_id = state

    def action_ar_approve(self):
        state = self._get_state('manager_approval')
        if state:
            self.stage_id = state

    def action_manager_approve(self):
        state = self._get_state('partnership')
        # state = self._get_state('completed')
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
            if state:
                rec.stage_id = state

    def action_cancel(self):
        state = self._get_state('cancelled')
        if state:
            self.stage_id = state

    def action_view_documents(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [('res_model', '=', 'dealer.application'), ('res_id', '=', self.id)],
            'context': {'default_res_model': 'dealer.application', 'default_res_id': self.id}
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
                'is_dealer': False,
            })
            self.partner_id = partner.id

            portal_wizard = self.env['portal.wizard'].with_context(
                active_ids=partner.ids,
                active_model='res.partner',
            ).create({})

            wizard_user = portal_wizard.user_ids.filtered(
                lambda u: u.partner_id == partner
            )
            if wizard_user:
                wizard_user.action_grant_access()

        return self.partner_id

    @api.depends()
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'dealer.application'),
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
                vals['name'] = self.env['ir.sequence'].next_by_code('dealer.application') or 'New'
            if not vals.get('access_token'):
                vals['access_token'] = secrets.token_urlsafe(32)
        return super().create(vals_list)

    def action_create_partnership_fee_order(self):
        self.ensure_one()
        if self.partnership_order_id:
            raise ValidationError("A partnership fee order has already been created.")
        
        fee_product = self.env['product.product'].search([
            ('is_partnership_fee', '=', True)
        ], limit=1)
        
        if not fee_product:
            raise ValidationError("No partnership fee product found. Please mark a product with 'Partnership Fee Product'.")
        
        if not self.partner_id:
            raise ValidationError("Please set a partner before creating the order.")
        
        order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
        })
        self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': fee_product.id,
            'product_uom_qty': 1,
            'price_unit': 350.0,
        })
        self.partnership_order_id = order.id
        
    def action_complete_partnership(self):
        state = self._get_state('completed')
        for rec in self:
            if not rec.partnership_order_id:
                raise ValidationError("Please create the $350 partnership fee order before completing onboarding.")
            if state:
                rec.stage_id = state