from odoo import models, fields, api


class DealerDashboard(models.Model):
    _name = 'dealer.dashboard'
    _description = 'Dealer Sales Rep Dashboard'

    name = fields.Char(default='Dashboard')

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    total_leads = fields.Integer(compute='_compute_data')
    my_applications = fields.Integer(compute='_compute_data')
    won_leads = fields.Integer(compute='_compute_data')
    pipeline_leads = fields.Integer(compute='_compute_data')

    dashboard_graph_data = fields.Text(compute='_compute_graph')
    
    @api.model
    def create_dashboard_for_user(self):
        if not self.search([('user_id', '=', self.env.user.id)]):
            self.create({'user_id': self.env.user.id})

    def _compute_data(self):
        for rec in self:
            user = rec.env.user

            rec.total_leads = self.env['crm.lead'].search_count([
                ('user_id', '=', user.id)
            ])

            rec.my_applications = self.env['crm.application'].search_count([
                ('lead_id.user_id', '=', user.id)
            ])

            rec.won_leads = self.env['crm.lead'].search_count([
                ('user_id', '=', user.id),
                ('stage_id.is_won', '=', True)
            ])

            rec.pipeline_leads = self.env['crm.lead'].search_count([
                ('user_id', '=', user.id),
                ('stage_id.is_won', '=', False)
            ])

    def _compute_graph(self):
        for rec in self:
            user = self.env.user

            leads = self.env['crm.lead'].search([
                ('user_id', '=', user.id)
            ])

            stage_data = {}
            for lead in leads:
                stage = lead.stage_id.name
                stage_data[stage] = stage_data.get(stage, 0) + 1

            rec.dashboard_graph_data = {
                'labels': list(stage_data.keys()),
                'datasets': [{
                    'label': 'Leads by Stage',
                    'data': list(stage_data.values()),
                }]
            }

    # ACTION BUTTONS
    def action_view_leads(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Leads',
            'res_model': 'crm.lead',
            'view_mode': 'kanban,list,form',
            'domain': [('user_id', '=', self.env.user.id)],
        }

    def action_view_applications(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Applications',
            'res_model': 'crm.application',
            'view_mode': 'kanban,list,form',
            'domain': [('lead_id.user_id', '=', self.env.user.id)],
        }

    def action_view_pipeline(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pipeline',
            'res_model': 'crm.lead',
            'view_mode': 'kanban,list,form',
            'domain': [
                ('user_id', '=', self.env.user.id),
                ('stage_id.is_won', '=', False)
            ],
        }

    def action_view_won(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Won Deals',
            'res_model': 'crm.lead',
            'view_mode': 'kanban,list,form',
            'domain': [
                ('user_id', '=', self.env.user.id),
                ('stage_id.is_won', '=', True)
            ],
        }