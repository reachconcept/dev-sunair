from odoo import models, fields


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    pipeline_type = fields.Selection([
        ('all', 'All Pipelines'),
        ('regular', 'Regular CRM Only'),
        ('dealer', 'Dealer Requests Only'),
    ], string='Pipeline', default='all', required=True)
