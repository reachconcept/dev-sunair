from odoo import models, fields

class CustomerType(models.Model):
    _name = 'customer.type'
    _description = 'Customer Type'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    tag_ids = fields.Many2many(
        'crm.tag',
        'customer_type_crm_tag_rel',
        'customer_type_id',
        'tag_id',
        string='Tags'
    )
