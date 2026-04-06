from odoo import models, fields


class DealerRequestState(models.Model):
    _name = 'dealer.request.state'
    _description = 'Dealer Request State'
    _order = 'sequence, id'

    name = fields.Char(string='State Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Folded in Kanban', default=False)
    is_closed = fields.Boolean(string='Closing State', default=False,
                               help='Requests in this state are considered closed/final.')
    color = fields.Integer(string='Color Index')
