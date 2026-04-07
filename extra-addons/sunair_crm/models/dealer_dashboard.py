# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class DealerApplicationDashboard(models.Model):
    _inherit = 'dealer.application'

    @api.model
    def get_dashboard_data(self, period='all'):
        try:
            return self._build_dashboard_data(period)
        except Exception as e:
            _logger.error("get_dashboard_data error: %s", e, exc_info=True)
            return self._dashboard_empty()

    def _build_dashboard_data(self, period='all'):
        now = datetime.now()

        # ── Period → date_from ──────────────────────────────
        if period == '7':
            date_from = now - timedelta(days=7)
        elif period == '30':
            date_from = now - timedelta(days=30)
        elif period == '90':
            date_from = now - timedelta(days=90)
        elif period == 'year':
            date_from = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            date_from = None  # all time

        date_from_str = date_from.strftime('%Y-%m-%d 00:00:00') if date_from else None

        # ── Dealers ─────────────────────────────────────────
        dealer_domain = [('is_dealer', '=', True)]
        if date_from_str:
            dealer_domain += [('create_date', '>=', date_from_str)]

        dealers       = self.env['res.partner'].search(dealer_domain)
        all_dealers   = self.env['res.partner'].search([('is_dealer', '=', True)])
        total         = len(dealers)
        active        = len(dealers.filtered('active'))

        # New this month / quarter (always relative to now, not period)
        month_start   = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        q_month       = ((now.month - 1) // 3) * 3 + 1
        quarter_start = now.replace(month=q_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        new_month     = len(all_dealers.filtered(lambda p: p.create_date and p.create_date >= month_start))
        new_quarter   = len(all_dealers.filtered(lambda p: p.create_date and p.create_date >= quarter_start))

        # ── Applications ────────────────────────────────────
        app_domain = []
        if date_from_str:
            app_domain += [('create_date', '>=', date_from_str)]
        apps       = self.env['dealer.application'].search(app_domain)
        app_funnel = self._dash_group_by(apps, lambda r: r.stage_id.name if r.stage_id else 'No Stage')

        # ── Requests ────────────────────────────────────────
        req_domain = []
        if date_from_str:
            req_domain += [('create_date', '>=', date_from_str)]
        reqs           = self.env['dealer.request'].search(req_domain)
        request_states = self._dash_group_by(reqs, lambda r: r.state_id.name if r.state_id else 'No State')

        # ── Territory ────────────────────────────────────────
        territory_data = self._dash_group_by(
            apps.filtered('territory_id'),
            lambda r: r.territory_id.name,
        )

        # ── Product lines ────────────────────────────────────
        pl_all            = self.env['dealer.product.line'].search([('partner_id', 'in', dealers.ids)])
        product_line_data = self._dash_group_by(
            pl_all, lambda r: r.product_line_id.name if r.product_line_id else 'Unknown'
        )

        # ── US state distribution ────────────────────────────
        state_data = self._dash_group_by(
            dealers,
            lambda p: (p.state_id.code or p.state_id.name) if p.state_id else 'Unknown',
        )[:10]

        # ── Monthly growth (last 6 months, always) ───────────
        monthly_growth = []
        for i in range(5, -1, -1):
            ref     = now - timedelta(days=30 * i)
            m_start = ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            m_end   = (now - timedelta(days=30 * (i - 1))).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0) if i > 0 else now
            count   = len(all_dealers.filtered(
                lambda p, s=m_start, e=m_end: p.create_date and s <= p.create_date <= e
            ))
            monthly_growth.append({'label': m_start.strftime('%b %Y'), 'count': count})

        # ── Knowledge levels ─────────────────────────────────
        rating_map     = {'0': 'Beginner', '1': 'Basic', '2': 'Intermediate', '3': 'Advanced', '4': 'Expert'}
        knowledge_dist = self._dash_group_by(pl_all, lambda r: rating_map.get(r.rating or '0', 'Unknown'))

        return {
            'kpis': {
                'total_dealers':      total,
                'active_dealers':     active,
                'inactive_dealers':   total - active,
                'new_this_month':     new_month,
                'new_this_quarter':   new_quarter,
                'total_applications': len(apps),
                'total_requests':     len(reqs),
            },
            'territory_data':    territory_data,
            'product_line_data': product_line_data,
            'state_data':        state_data,
            'app_funnel':        app_funnel,
            'request_states':    request_states,
            'monthly_growth':    monthly_growth,
            'knowledge_dist':    knowledge_dist,
        }

    @staticmethod
    def _dash_group_by(records, key_fn):
        counts = defaultdict(int)
        for r in records:
            try:
                counts[key_fn(r)] += 1
            except Exception:
                counts['Unknown'] += 1
        return sorted(
            [{'name': k, 'count': v} for k, v in counts.items()],
            key=lambda x: x['count'], reverse=True,
        )

    @staticmethod
    def _dashboard_empty():
        return {
            'kpis': {
                'total_dealers': 0, 'active_dealers': 0, 'inactive_dealers': 0,
                'new_this_month': 0, 'new_this_quarter': 0,
                'total_applications': 0, 'total_requests': 0,
            },
            'territory_data': [], 'product_line_data': [], 'state_data': [],
            'app_funnel': [], 'request_states': [], 'monthly_growth': [],
            'knowledge_dist': [],
        }