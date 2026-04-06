from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_dealer = fields.Boolean(string='Is Dealer', default=False, tracking=True)
    dealer_status_id = fields.Many2one('dealer.status', string='Dealer Status', tracking=True, ondelete='set null')
    dealer_status_color = fields.Integer(related='dealer_status_id.color', string='Dealer Status Color')
    territory_id = fields.Many2one('crm.territory', string='Territory', tracking=True)
    dealer_representative_id = fields.Many2one('res.users', string='Dealer Representative', tracking=True)
    product_line_ids = fields.One2many(
        'product.line.mapping',
        'partner_id',
        string='Product Lines',
    )