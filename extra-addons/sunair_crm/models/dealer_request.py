from odoo import models, fields, api


class DealerRequest(models.Model):
    _name = 'dealer.request'
    _description = 'Dealer Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    state_id = fields.Many2one(
        'dealer.request.state',
        string='State',
        tracking=True,
        ondelete='set null',
        group_expand='_read_group_state_ids',
    )
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked'),
    ], string='Kanban State', default='normal', tracking=True)

    # Contact Information
    first_name = fields.Char(string='First Name', tracking=True)
    last_name = fields.Char(string='Last Name', tracking=True)
    title = fields.Char(string='Title')
    company = fields.Char(string='Company')
    street = fields.Char(string='Address')
    city = fields.Char(string='City')
    country_state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id.code', '=', 'US')]")
    zip = fields.Char(string='Zip Code')
    work_phone = fields.Char(string='Work Phone')
    email = fields.Char(string='Email')

    # Business Type (multi-checkbox)
    is_distributor = fields.Boolean(string='Distributor')
    is_retail = fields.Boolean(string='Retail')
    is_wholesale = fields.Boolean(string='Wholesale')

    # Business Background
    years_in_business = fields.Char(string='How Long in Business')
    has_showroom = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Do You Have a Showroom?', default='no')
    how_heard = fields.Char(string='How Did You Hear About Sunair?')
    comments = fields.Text(string='Comments')

    # Retractable Awnings
    sells_retractable_awnings = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Do You Currently Sell Retractable Awnings?', default='no')
    retractable_awnings_supplier = fields.Char(string='Retractable Awnings Supplier')
    retractable_awnings_sales_pct = fields.Selection([
        ('0_10', '0% - 10%'),
        ('11_25', '11% - 25%'),
        ('26_50', '26% - 50%'),
        ('51_75', '51% - 75%'),
        ('76_100', '76% - 100%'),
    ], string='Current Percentage of Awning Sales', default='0_10')

    # Solar Screens
    sells_solar_screens = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Do You Currently Sell Solar Screens?', default='no')
    solar_screens_supplier = fields.Char(string='Solar Screens Supplier')
    solar_screens_sales_pct = fields.Selection([
        ('0_10', '0% - 10%'),
        ('11_25', '11% - 25%'),
        ('26_50', '26% - 50%'),
        ('51_75', '51% - 75%'),
        ('76_100', '76% - 100%'),
    ], string='Current Percentage of Solar Screen Sales', default='0_10')
    solar_screens_type = fields.Selection([
        ('exterior', 'Exterior'),
        ('interior', 'Interior'),
        ('both', 'Both'),
    ], string='Solar Screen Type', default='exterior')

    # Pergola / Adjustable Louvered Systems
    sells_pergola_louvered = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Do You Currently Sell Pergola Awnings or Adjustable Louvered Systems?', default='no')
    pergola_louvered_supplier = fields.Char(string='Pergola / Louvered Systems Supplier')
    pergola_louvered_sales_pct = fields.Selection([
        ('0_10', '0% - 10%'),
        ('11_25', '11% - 25%'),
        ('26_50', '26% - 50%'),
        ('51_75', '51% - 75%'),
        ('76_100', '76% - 100%'),
    ], string='Current Percentage of Pergola / Louvered Systems Sales', default='0_10')

    # Relations
    lead_id = fields.Many2one('crm.lead', string='Lead', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    dealer_representative_id = fields.Many2one('res.users', string='Dealer Representative', tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    application_id = fields.Many2one('dealer.application', string='Application', readonly=True, copy=False)

    application_count = fields.Integer(compute='_compute_application_count')

    # Fields that are kept in sync with dealer.application (request field -> application field)
    _SYNC_TO_APPLICATION = {
        'company':           'company_legal_name',
        'street':            'street',
        'city':              'city',
        'country_state_id':  'state_id',
        'zip':               'zip_code',
        'work_phone':        'phone',
        'email':             'email',
        'partner_id':        'partner_id',
        'lead_id':           'lead_id',
    }

    def _compute_application_count(self):
        for rec in self:
            rec.application_count = 1 if rec.application_id else 0

    def action_view_application(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dealer Application',
            'res_model': 'dealer.application',
            'view_mode': 'form',
            'res_id': self.application_id.id,
            'target': 'current',
        }

    def action_create_application(self):
        self.ensure_one()
        if self.application_id:
            return self.action_view_application()
        application = self.env['dealer.application'].create({
            'company_legal_name': self.company,
            'street': self.street,
            'city': self.city,
            'state_id': self.country_state_id.id,
            'zip_code': self.zip,
            'phone': self.work_phone,
            'email': self.email,
            'lead_id': self.lead_id.id,
            'partner_id': self.partner_id.id,
            'request_id': self.id,
        })
        self.application_id = application.id
        application.message_post(
            body=f'Application created from Dealer Request <a href="/odoo/dealer-requests/{self.id}">{self.name}</a>.'
        )
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dealer Application',
            'res_model': 'dealer.application',
            'view_mode': 'form',
            'res_id': application.id,
            'target': 'current',
        }

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get('dealer_sync_skip'):
            return res
        sync_vals = {
            app_field: vals[req_field]
            for req_field, app_field in self._SYNC_TO_APPLICATION.items()
            if req_field in vals
        }
        if sync_vals:
            for rec in self:
                if rec.application_id:
                    rec.application_id.with_context(dealer_sync_skip=True).write(sync_vals)
        return res

    @api.model
    def _read_group_state_ids(self, states, _domain):
        return states.search([])

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('dealer.request') or 'New'
        return super().create(vals_list)
