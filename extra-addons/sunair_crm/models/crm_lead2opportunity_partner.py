from odoo import models, fields, api


class CrmLead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    customer_type_id = fields.Many2one('customer.type')
    lead_type_id = fields.Many2one('lead.type')
    territory_id = fields.Many2one('crm.territory', readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        lead = self.env['crm.lead'].browse(self.env.context.get('active_id'))

        if lead:
            res.update({
                'customer_type_id': lead.customer_type_id.id,
                'lead_type_id': lead.lead_type_id.id,
                'territory_id': lead.territory_id.id,
            })
        return res

    def _action_convert(self):
        result = super()._action_convert()
        for rec in self:
            lead = rec.lead_id
            lead.write({
                'customer_type_id': rec.customer_type_id.id,
                'lead_type_id': rec.lead_type_id.id,
            })
        return result