from odoo import models, fields, api


class DealerActivity(models.Model):
    _name = 'dealer.activity'
    _description = 'Dealer Activity'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _rec_name = 'subject'

    subject = fields.Char(string='Subject', required=True, tracking=True)
    partner_id = fields.Many2one(
        'res.partner', string='Dealer', required=True,
        domain=[('is_dealer', '=', True)], tracking=True
    )
    user_id = fields.Many2one(
        'res.users', string='Salesperson', required=True,
        default=lambda self: self.env.user, tracking=True
    )
    date = fields.Date(string='Date', required=True, default=fields.Date.today, tracking=True)
    contact_method = fields.Selection([
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('online_meeting', 'Online Meeting'),
        ('office_visit', 'Office Visit'),
        ('other', 'Other'),
    ], string='Contact Method', required=True, tracking=True)
    state = fields.Selection([
        ('planned', 'Planned'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='planned', required=True, tracking=True)
    notes = fields.Html(string='Notes')

    def action_mark_done(self):
        self.write({'state': 'done'})

    def action_mark_cancelled(self):
        self.write({'state': 'cancelled'})

    def action_reset_planned(self):
        self.write({'state': 'planned'})
