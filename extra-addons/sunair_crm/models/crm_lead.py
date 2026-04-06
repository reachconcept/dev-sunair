from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    customer_type_id = fields.Many2one('customer.type', string='Customer Type')
    lead_type_id = fields.Many2one('lead.type', string='Lead Type')
    is_dealer_pipeline = fields.Boolean(related='lead_type_id.is_dealer_pipeline', store=True, readonly=True)
    crm_product_category_id = fields.Many2one('crm.product.category', string='Product Category')

    territory_id = fields.Many2one(
        'crm.territory',
        string='Territory',
        compute='_compute_territory',
        store=True,
        readonly=True
    )
    tag_ids = fields.Many2many('crm.tag',string='Tags',domain="[('id', 'in', allowed_tag_ids)]")
    allowed_tag_ids = fields.Many2many('crm.tag',compute='_compute_allowed_tag_ids',store=False)
    application_count = fields.Integer(compute='_compute_application_count')
    
    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if 'country_id' in fields_list and 'country_id' not in defaults:
            us = self.env['res.country'].search([('code', '=', 'US')], limit=1)
            if us:
                defaults['country_id'] = us.id
        return defaults

    @api.depends('customer_type_id')
    def _compute_allowed_tag_ids(self):
        for rec in self:
            rec.allowed_tag_ids = rec.customer_type_id.tag_ids if rec.customer_type_id else False

    @api.depends('zip')
    def _compute_territory(self):
        territories = self.env['crm.territory'].search([('active', '=', True)])

        for rec in self:
            rec.territory_id = False
            rec.team_id = False
            rec.user_id = False

            if rec.zip and len(rec.zip) >= 3:
                try:
                    prefix = int(rec.zip[:3])
                except:
                    continue

                for territory in territories:
                    if territory.zip_range:
                        ranges = territory.zip_range.split(',')

                        for r in ranges:
                            if '-' in r:
                                start, end = r.split('-')
                                try:
                                    if int(start) <= prefix <= int(end):
                                        rec.territory_id = territory.id
                                        rec.team_id = territory.team_id.id
                                        rec.user_id = territory.team_id.user_id.id if territory.team_id.user_id else False
                                        break
                                except:
                                    continue
                        if rec.territory_id:
                            break
                        
    def _compute_application_count(self):
        for rec in self:
            rec.application_count = self.env['dealer.application'].search_count([
                ('lead_id', '=', rec.id)
            ])
            
    def action_create_application(self):
        app = self.env['dealer.application'].create({
            'lead_id': self.id,
            'partner_id': self.partner_id.id,
            'company_legal_name': self.partner_name,
            'state': 'draft',
            'street': self.street + (' ' + self.street2 if self.street2 else ''),
            'city': self.city,
            'state_id': self.state_id.id,
            'zip_code': self.zip,
            'email': self.email_from,
            'phone': self.phone,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Application',
            'res_model': 'dealer.application',
            'view_mode': 'form',
            'res_id': app.id,
            'target': 'current',
        }

    def action_view_applications(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Applications',
            'res_model': 'dealer.application',
            'view_mode': 'kanban,list,form',
            'domain': [('lead_id', '=', self.id)],
        }