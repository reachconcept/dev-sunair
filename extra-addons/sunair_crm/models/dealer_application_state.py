from odoo import models, fields


class DealerApplicationState(models.Model):
    _name = 'dealer.application.state'
    _description = 'Dealer Application State'
    _order = 'sequence, id'

    name = fields.Char(string='State Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Folded in Kanban', default=False)
    is_closed = fields.Boolean(
        string='Closing State', default=False,
        help='Applications in this state are considered finalized.',
    )
    color = fields.Integer(string='Color Index')
    state_type = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('submitted', 'Submitted'),
        ('ar_approval', 'AR Approval'),
        ('manager_approval', 'Manager Approval'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='State Type',
       help='Drives workflow button visibility and internal transitions.')
