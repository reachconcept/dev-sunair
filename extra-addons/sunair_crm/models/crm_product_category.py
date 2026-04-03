from odoo import models, fields

class CrmProductCategory(models.Model):
    _name = 'crm.product.category'
    _description = 'CRM Product Category'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)