from odoo import models, fields, api


class CrmTerritory(models.Model):
    _name = 'crm.territory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'CRM Territory'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(string='Territory Code', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    team_id = fields.Many2one('crm.team', string='Primary Sales Team', required=True)
    dealer_representative_id = fields.Many2one('res.users', string='Representative', tracking=True)
    backup_user_id = fields.Many2one('res.users', string='Backup Representative', compute='_compute_backup_user', store=True)
    zip_range = fields.Char(string='ZIP Code Range', help='Define ZIP code ranges for this territory, e.g. "100-199,300-399"')
    state_ids = fields.Many2many(
        'res.country.state',
        'crm_territory_state_rel',
        'territory_id',
        'state_id',
        string='States',
        domain="[('country_id.code', '=', 'US')]"
    )
    active = fields.Boolean(default=True)
    auto_assign = fields.Boolean(string='Lead Auto Assignment')
    lead_count = fields.Integer(compute='_compute_lead_count')

    def _compute_lead_count(self):
        for rec in self:
            rec.lead_count = self.env['crm.lead'].search_count([
                ('territory_id', '=', rec.id)
            ])

    def action_view_leads(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Leads',
            'res_model': 'crm.lead',
            'view_mode': 'kanban,list,form',
            'domain': [('territory_id', '=', self.id)],
            'context': {'default_territory_id': self.id},
        }

    @api.depends('team_id')
    def _compute_backup_user(self):
        for rec in self:
            rec.backup_user_id = rec.team_id.user_id.id if rec.team_id else False

    def get_matching_territory(self, partner_state_id=None, partner_zip=None):
        territories = self.search([('active', '=', True), ('auto_assign', '=', True)])

        if partner_state_id:
            for territory in territories:
                if partner_state_id in territory.state_ids.ids:
                    return territory

        if partner_zip:
            try:
                zip_int = int(partner_zip.strip())
            except (ValueError, AttributeError):
                zip_int = None

            if zip_int is not None:
                for territory in territories:
                    if territory._zip_matches(zip_int):
                        return territory

        return self.browse()

    def _zip_matches(self, zip_int):
        self.ensure_one()
        if not self.zip_range:
            return False
        for segment in self.zip_range.split(','):
            segment = segment.strip()
            if '-' in segment:
                parts = segment.split('-', 1)
                try:
                    lo, hi = int(parts[0].strip()), int(parts[1].strip())
                    if lo <= zip_int <= hi:
                        return True
                except ValueError:
                    continue
            else:
                try:
                    if zip_int == int(segment):
                        return True
                except ValueError:
                    continue
        return False