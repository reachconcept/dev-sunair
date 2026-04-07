from odoo import models, fields, api


class DealerMatchWizard(models.TransientModel):
    _name = 'crm.lead.dealer.match.wizard'
    _description = 'Find Best Dealer for Lead'

    lead_id = fields.Many2one('crm.lead', required=True, readonly=True)
    zip_code = fields.Char(related='lead_id.zip', string='ZIP Code', readonly=True)
    territory_id = fields.Many2one(related='lead_id.territory_id', string='Territory', readonly=True)

    product_line_ids = fields.Many2many(
        'product.line',
        string='Required Product Lines',
        help='Select the product lines this lead requires. Dealers will be scored based on how many they carry and their expertise rating.',
    )

    result_ids = fields.One2many(
        'crm.lead.dealer.match.line',
        'wizard_id',
        string='Matched Dealers',
    )

    matched = fields.Boolean(default=False)

    def action_find_dealers(self):
        self.ensure_one()

        # Clear previous results
        self.result_ids.unlink()

        lead = self.lead_id
        selected_lines = self.product_line_ids

        # --- Find dealers in the same territory ---
        domain = [('is_dealer', '=', True)]
        if lead.territory_id:
            domain.append(('territory_id', '=', lead.territory_id.id))

        dealers = self.env['res.partner'].search(domain)

        # --- Build win rate map via read_group (avoid N+1) ---
        Lead = self.env['crm.lead'].with_context(active_test=False)
        total_data = Lead.read_group(
            [('dealer_id', 'in', dealers.ids)],
            ['dealer_id'], ['dealer_id'],
        )
        won_data = Lead.read_group(
            [('dealer_id', 'in', dealers.ids), ('stage_id.is_won', '=', True)],
            ['dealer_id'], ['dealer_id'],
        )
        totals = {r['dealer_id'][0]: r['dealer_id_count'] for r in total_data}
        wons = {r['dealer_id'][0]: r['dealer_id_count'] for r in won_data}

        # --- Score each dealer ---
        lines_to_create = []
        selected_ids = selected_lines.ids

        for dealer in dealers:
            # Build a map of product_line_id -> rating for this dealer
            pl_map = {
                m.product_line_id.id: int(m.rating or '0')
                for m in dealer.product_line_ids
            }

            matched_count = 0
            score = 0
            for pl_id in selected_ids:
                if pl_id in pl_map:
                    matched_count += 1
                    score += pl_map[pl_id]

            # Skip dealers with zero match when product lines are selected
            if selected_ids and matched_count == 0:
                continue

            total = totals.get(dealer.id, 0)
            won = wons.get(dealer.id, 0)
            win_rate = (won / total * 100.0) if total else 0.0

            lines_to_create.append({
                'wizard_id': self.id,
                'partner_id': dealer.id,
                'score': score,
                'matched_line_count': matched_count,
                'total_line_count': len(selected_ids),
                'lead_count': total,
                'won_lead_count': won,
                'win_rate': win_rate,
            })

        # Sort by score desc, then win_rate desc
        lines_to_create.sort(key=lambda r: (r['score'], r['win_rate']), reverse=True)
        self.env['crm.lead.dealer.match.line'].create(lines_to_create)
        self.matched = True

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_assign_dealer(self):
        self.ensure_one()
        selected = self.result_ids.filtered('selected')
        if not selected:
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
        dealer = selected[0].partner_id
        lead = self.lead_id
        lead.dealer_id = dealer

        lines_summary = ', '.join(pl.name for pl in self.product_line_ids) or 'N/A'
        lead.message_post(
            body=(
                f'Dealer assigned via Best Dealer Wizard.\n'
                f'Dealer: {dealer.name}\n'
                f'Territory: {dealer.territory_id.name or "N/A"}\n'
                f'Product Lines: {lines_summary}\n'
                f'Score: {selected[0].score} | Coverage: {selected[0].coverage} | Win Rate: {selected[0].win_rate:.1f}%'
            ),
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )
        return {'type': 'ir.actions.act_window_close'}


class DealerMatchLine(models.TransientModel):
    _name = 'crm.lead.dealer.match.line'
    _description = 'Dealer Match Result Line'
    _order = 'score desc, win_rate desc'

    wizard_id = fields.Many2one('crm.lead.dealer.match.wizard', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Dealer', readonly=True)
    territory_id = fields.Many2one(related='partner_id.territory_id', string='Territory', readonly=True)
    dealer_status_id = fields.Many2one(related='partner_id.dealer_status_id', string='Status', readonly=True)

    score = fields.Integer(string='Score', readonly=True)
    matched_line_count = fields.Integer(string='Matched', readonly=True)
    total_line_count = fields.Integer(string='Required', readonly=True)
    coverage = fields.Char(string='Coverage', compute='_compute_coverage')

    lead_count = fields.Integer(string='Leads', readonly=True)
    won_lead_count = fields.Integer(string='Won', readonly=True)
    win_rate = fields.Float(string='Win Rate %', readonly=True, digits=(5, 1))

    selected = fields.Boolean(string='Select', default=False)

    @api.depends('matched_line_count', 'total_line_count')
    def _compute_coverage(self):
        for rec in self:
            if rec.total_line_count:
                pct = int(rec.matched_line_count / rec.total_line_count * 100)
                rec.coverage = f'{rec.matched_line_count}/{rec.total_line_count} ({pct}%)'
            else:
                rec.coverage = '—'

    @api.onchange('selected')
    def _onchange_selected(self):
        # Allow only one selection at a time
        if self.selected:
            for line in self.wizard_id.result_ids:
                if line != self and line.selected:
                    line.selected = False
