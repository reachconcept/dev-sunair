from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_dealer_starter_kit = fields.Boolean()
    is_partnership_fee = fields.Boolean(string='Partnership Fee Product', default=False)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_dealer_starter_kit = fields.Boolean(related='product_tmpl_id.is_dealer_starter_kit', store=True)
    is_partnership_fee = fields.Boolean(related='product_tmpl_id.is_partnership_fee', store=True)
