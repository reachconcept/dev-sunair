from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_dealer = fields.Boolean(string='Is Dealer', default=False, tracking=True)