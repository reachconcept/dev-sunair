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