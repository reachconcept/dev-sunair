from odoo import models, fields


class DealerStatus(models.Model):
    _name = 'dealer.status'
    _description = 'Dealer Status'
    _order = 'sequence, id'

    name = fields.Char(string='Status Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string='Color Index')
    fold = fields.Boolean(string='Folded in Kanban', default=False)
