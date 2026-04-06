from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_dealer = fields.Boolean(string='Is Dealer', default=False, tracking=True)
    dealer_status_id = fields.Many2one('dealer.status', string='Dealer Status', tracking=True, ondelete='set null')
    dealer_status_color = fields.Integer(related='dealer_status_id.color', string='Dealer Status Color')
    territory_id = fields.Many2one('crm.territory', string='Territory', tracking=True)
    dealer_representative_id = fields.Many2one('res.users', string='Representative', tracking=True)
    product_line_ids = fields.One2many('dealer.product.line', 'partner_id', string='Product Lines')

    dealer_activity_count = fields.Integer(compute='_compute_dealer_activity_count')
    dealer_lead_count = fields.Integer(compute='_compute_dealer_lead_stats')
    dealer_won_lead_count = fields.Integer(compute='_compute_dealer_lead_stats')
    dealer_win_rate = fields.Float(compute='_compute_dealer_lead_stats', digits=(5, 1))

    available_product_line_ids = fields.Many2many(
        'product.line',
        compute='_compute_available_product_line_ids',
    )

    product_line_kanban_html = fields.Html(
        compute='_compute_product_line_kanban_html',
        sanitize=False,
    )
    dealer_iq_html = fields.Html(
        compute='_compute_dealer_iq_html',
        sanitize=False,
    )

    def _compute_dealer_lead_stats(self):
        Lead = self.env['crm.lead'].with_context(active_test=False)
        # total (active + inactive)
        total_data = Lead.read_group(
            [('dealer_id', 'in', self.ids)],
            ['dealer_id'], ['dealer_id'],
        )
        totals = {row['dealer_id'][0]: row['dealer_id_count'] for row in total_data}
        # won
        won_data = Lead.read_group(
            [('dealer_id', 'in', self.ids), ('stage_id.is_won', '=', True)],
            ['dealer_id'], ['dealer_id'],
        )
        wons = {row['dealer_id'][0]: row['dealer_id_count'] for row in won_data}
        for rec in self:
            total = totals.get(rec.id, 0)
            won = wons.get(rec.id, 0)
            rec.dealer_lead_count = total
            rec.dealer_won_lead_count = won
            rec.dealer_win_rate = (won / total * 100.0) if total else 0.0

    def action_view_dealer_leads(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Leads',
            'res_model': 'crm.lead',
            'view_mode': 'list,kanban,form',
            'domain': [('dealer_id', '=', self.id)],
            'context': {'default_dealer_id': self.id},
        }

    def _compute_dealer_activity_count(self):
        data = self.env['dealer.activity'].read_group(
            [('partner_id', 'in', self.ids)],
            ['partner_id'],
            ['partner_id'],
        )
        counts = {row['partner_id'][0]: row['partner_id_count'] for row in data}
        for rec in self:
            rec.dealer_activity_count = counts.get(rec.id, 0)

    def action_view_dealer_activities(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dealer Activities',
            'res_model': 'dealer.activity',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    @api.depends('product_line_ids.product_line_id')
    def _compute_available_product_line_ids(self):
        all_lines = self.env['product.line'].search([])
        for rec in self:
            rec.available_product_line_ids = all_lines - rec.product_line_ids.product_line_id

    @api.depends(
        'dealer_lead_count', 'dealer_won_lead_count', 'dealer_win_rate',
        'dealer_activity_count', 'product_line_ids', 'dealer_status_id',
        'territory_id', 'dealer_representative_id',
    )
    def _compute_dealer_iq_html(self):
        for rec in self:
            if not rec.is_dealer:
                rec.dealer_iq_html = ''
                continue

            bullets = []

            # Leads insight
            total = rec.dealer_lead_count
            won = rec.dealer_won_lead_count
            lost = total - won
            rate = rec.dealer_win_rate
            if total:
                rate_color = '#20c997' if rate >= 66 else '#f0a500' if rate >= 33 else '#e74c3c'
                bullets.append((
                    rate_color,
                    f'{total} lead{"s" if total != 1 else ""} assigned — '
                    f'<strong>{won} won</strong>, {lost} not won. '
                    f'Win rate: <strong style="color:{rate_color};">{rate:.1f}%</strong>.'
                ))
            else:
                bullets.append(('#adb5bd', 'No leads assigned to this dealer yet.'))

            # Activity insight
            act = rec.dealer_activity_count
            if act:
                bullets.append(('#74b9ff', f'{act} dealer activit{"ies" if act != 1 else "y"} recorded.'))
            else:
                bullets.append(('#adb5bd', 'No dealer activities recorded yet.'))

            # Product lines insight
            pl_count = len(rec.product_line_ids)
            if pl_count:
                names = ', '.join(l.product_line_id.name for l in rec.product_line_ids[:3])
                more = f' and {pl_count - 3} more' if pl_count > 3 else ''
                bullets.append(('#a29bfe', f'Carries <strong>{pl_count}</strong> product line{"s" if pl_count != 1 else ""}: {names}{more}.'))
            else:
                bullets.append(('#adb5bd', 'No product lines assigned yet.'))

            # Territory / rep
            parts = []
            if rec.territory_id:
                parts.append(f'territory <strong>{rec.territory_id.name}</strong>')
            if rec.dealer_representative_id:
                parts.append(f'rep <strong>{rec.dealer_representative_id.name}</strong>')
            if parts:
                bullets.append(('#fd79a8', f'Assigned to {" · ".join(parts)}.'))

            rows = ''.join(
                f'<div style="display:flex; align-items:flex-start; gap:10px; margin-bottom:6px;">'
                f'<span style="width:8px; height:8px; border-radius:50%; background:{color}; flex-shrink:0; margin-top:4px;"></span>'
                f'<span style="font-size:12px; color:#374151; line-height:1.5;">{text}</span>'
                f'</div>'
                for color, text in bullets
            )

            rec.dealer_iq_html = f'''
<div style="display:flex; align-items:flex-start; gap:14px;">
  <div style="width:40px; height:40px; border-radius:10px; background:#ede9fe;
              display:flex; align-items:center; justify-content:center; flex-shrink:0;">
    <i class="fa fa-lightbulb-o" style="font-size:20px; color:#6c63ff;"></i>
  </div>
  <div style="flex:1;">
    <div style="font-size:13px; font-weight:700; color:#1e1b4b; margin-bottom:10px; letter-spacing:0.3px;">
      Dealer Details <span style="font-size:10px; font-weight:400; color:#6c63ff;
        background:#ede9fe; padding:1px 7px; border-radius:10px; margin-left:4px;">insights</span>
    </div>
    {rows}
  </div>
</div>'''

    @api.depends('product_line_ids.product_line_id', 'product_line_ids.rating')
    def _compute_product_line_kanban_html(self):
        for rec in self:
            if not rec.product_line_ids:
                rec.product_line_kanban_html = ''
                continue
            rows = []
            for line in rec.product_line_ids:
                rating = int(line.rating or '0')
                filled = ''.join(
                    '<i class="fa fa-star" style="color:#f0a500; font-size:10px;"></i>'
                    for _ in range(rating)
                )
                empty = ''.join(
                    '<i class="fa fa-star-o" style="color:#dee2e6; font-size:10px;"></i>'
                    for _ in range(4 - rating)
                )
                label = dict(line._fields['rating'].selection).get(line.rating or '0', '')
                rows.append(
                    f'<div style="display:flex; justify-content:space-between; align-items:center;'
                    f' padding:3px 0; border-bottom:1px solid #f0f0f0; gap:6px;">'
                    f'<span style="font-size:12px; font-weight:500; white-space:nowrap; overflow:hidden;'
                    f' text-overflow:ellipsis;">{line.product_line_id.name}</span>'
                    f'<span style="display:flex; align-items:center; gap:1px; flex-shrink:0;"'
                    f' title="{label}">{filled}{empty}</span>'
                    f'</div>'
                )
            rec.product_line_kanban_html = (
                '<div style="margin-top:6px;">' + ''.join(rows) + '</div>'
            )
