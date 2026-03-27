from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    customer_type_id = fields.Many2one('customer.type', string='Customer Type')
    lead_type_id = fields.Many2one('lead.type', string='Lead Type')
    territory_id = fields.Many2one('crm.territory', string='Territory',compute='_compute_territory',store=True, readonly=True)

    tag_ids = fields.Many2many(
        'crm.tag',
        string='Tags',
        domain="[('id', 'in', allowed_tag_ids)]"
    )
    allowed_tag_ids = fields.Many2many('crm.tag',string='Allowed Tags',compute='_compute_allowed_tag_ids',store=False)
    @api.depends('customer_type_id')
    def _compute_allowed_tag_ids(self):
        for rec in self:
            if rec.customer_type_id and rec.customer_type_id.tag_ids:
                rec.allowed_tag_ids = rec.customer_type_id.tag_ids
            else:
                rec.allowed_tag_ids = False
            
    @api.depends('zip')
    def _compute_territory(self):
        territories = self.env['crm.territory'].search([('active', '=', True)])

        for rec in self:
            rec.territory_id = False

            if rec.zip and len(rec.zip) >= 3:
                try:
                    prefix = int(rec.zip[:3])
                except:
                    continue

                for territory in territories:
                    if territory.zip_range and '-' in territory.zip_range:
                        start, end = territory.zip_range.split('-')
                        try:
                            if int(start) <= prefix <= int(end):
                                rec.territory_id = territory.id
                                break
                        except:
                            continue