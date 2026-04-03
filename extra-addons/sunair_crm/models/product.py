from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_dealer_starter_kit = fields.Boolean()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_dealer_starter_kit = fields.Boolean(related='product_tmpl_id.is_dealer_starter_kit', store=True)