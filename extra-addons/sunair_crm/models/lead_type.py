from odoo import models, fields

class LeadType(models.Model):
    _name = 'lead.type'
    _description = 'Lead Type'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    is_dealer_pipeline = fields.Boolean(string='Dealer Pipeline', default=False)
    