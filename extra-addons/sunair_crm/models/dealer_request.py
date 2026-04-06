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
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.model
    def _read_group_state_ids(self, states, _domain):
        return states.search([])

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('dealer.request') or 'New'
        return super().create(vals_list)
