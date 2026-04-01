from odoo import models, fields

class LeadType(models.Model):
    _name = 'lead.type'
    _description = 'Lead Type'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    
    
class SunairDashboard(models.Model):
    _name = 'sunair.dashboard'
    _description = 'Sunair CRM Dashboard'

    def action_open_dashboard(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'sunair_crm_dashboard',
            'name': 'SUNAIR CRM Dashboard',
        }