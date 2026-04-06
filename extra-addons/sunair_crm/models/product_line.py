from odoo import models, fields


class ProductLine(models.Model):
    _name = 'product.line'
    _description = 'Product Line'
    _order = 'sequence, name'

    name = fields.Char(string='Product Line', required=True, translate=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string='Color Index')

    dealer_count = fields.Integer(
        string='Dealers',
        compute='_compute_dealer_count',
    )

    def _compute_dealer_count(self):
        data = self.env['dealer.product.line'].read_group(
            [('product_line_id', 'in', self.ids)],
            ['product_line_id'],
            ['product_line_id'],
        )
        counts = {row['product_line_id'][0]: row['product_line_id_count'] for row in data}
        for rec in self:
            rec.dealer_count = counts.get(rec.id, 0)
