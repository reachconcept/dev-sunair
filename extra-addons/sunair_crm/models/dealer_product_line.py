from odoo import models, fields


class DealerProductLine(models.Model):
    _name = 'dealer.product.line'
    _description = 'Dealer Product Line'
    _order = 'partner_id, product_line_id'

    partner_id = fields.Many2one(
        'res.partner',
        string='Dealer',
        required=True,
        ondelete='cascade',
    )
    product_line_id = fields.Many2one(
        'product.line',
        string='Product Line',
        required=True,
        ondelete='cascade',
    )
    rating = fields.Selection([
        ('0', 'Beginner'),
        ('1', 'Basic'),
        ('2', 'Intermediate'),
        ('3', 'Advanced'),
        ('4', 'Expert')], string='Knowledge Level', tracking=True,
        index=True)
    notes = fields.Char(string='Notes')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            'unique_partner_product_line',
            'unique(partner_id, product_line_id)',
            'This product line is already assigned to this dealer.',
        )
    ]
