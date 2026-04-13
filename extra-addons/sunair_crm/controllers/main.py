from odoo import http
from odoo.http import request


class DealerRequestController(http.Controller):

    @http.route(['/become-a-dealer', '/'], type='http', auth='public', website=True, sitemap=True)
    def dealer_form(self, **kwargs):
        """Render the Become a Dealer form page."""
        states = request.env['res.country.state'].sudo().search([
            ('country_id.code', '=', 'US')
        ], order='name asc')
        return request.render('sunair_crm.dealer_request_form', {
            'states': states,
            'error': {},
            'values': {},
        })

    @http.route('/become-a-dealer/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def dealer_form_submit(self, **post):
        """Handle dealer form submission and create a dealer.request record."""
        error = {}
        # Required field validation
        required_fields = ['first_name', 'last_name', 'street', 'city', 'state_id', 'zip', 'email']
        for field in required_fields:
            if not post.get(field, '').strip():
                error[field] = True

        states = request.env['res.country.state'].sudo().search([
            ('country_id.code', '=', 'US')
        ], order='name asc')

        if error:
            return request.render('sunair_crm.dealer_request_form', {
                'states': states,
                'error': error,
                'values': post,
            })

        # Resolve state
        state_id = False
        if post.get('state_id'):
            try:
                state_id = int(post['state_id'])
            except (ValueError, TypeError):
                state_id = False

        vals = {
            # Contact
            'first_name':   post.get('first_name', '').strip(),
            'last_name':    post.get('last_name', '').strip(),
            'title':        post.get('title', '').strip(),
            'company':      post.get('company', '').strip(),
            'street':       post.get('street', '').strip(),
            'city':         post.get('city', '').strip(),
            'country_state_id': state_id,
            'zip':          post.get('zip', '').strip(),
            'work_phone':   post.get('work_phone', '').strip(),
            'email':        post.get('email', '').strip(),

            # Business type (checkboxes)
            'is_distributor': bool(post.get('is_distributor')),
            'is_retail':      bool(post.get('is_retail')),
            'is_wholesale':   bool(post.get('is_wholesale')),

            # Business background
            'years_in_business': post.get('years_in_business', '').strip(),
            'has_showroom':      post.get('has_showroom', 'no'),
            'how_heard':         post.get('how_heard', '').strip(),
            'comments':          post.get('comments', '').strip(),

            # Retractable awnings
            'sells_retractable_awnings':   post.get('sells_retractable_awnings', 'no'),
            'retractable_awnings_supplier': post.get('retractable_awnings_supplier', '').strip(),
            'retractable_awnings_sales_pct': post.get('retractable_awnings_sales_pct', '0_10'),

            # Solar screens
            'sells_solar_screens':   post.get('sells_solar_screens', 'no'),
            'solar_screens_supplier': post.get('solar_screens_supplier', '').strip(),
            'solar_screens_sales_pct': post.get('solar_screens_sales_pct', '0_10'),
            'solar_screens_type':     post.get('solar_screens_type', 'exterior'),

            # Pergola / Louvered
            'sells_pergola_louvered':   post.get('sells_pergola_louvered', 'no'),
            'pergola_louvered_supplier': post.get('pergola_louvered_supplier', '').strip(),
            'pergola_louvered_sales_pct': post.get('pergola_louvered_sales_pct', '0_10'),
        }

        request.env['dealer.request'].sudo().create([vals])

        return request.render('sunair_crm.dealer_request_success', {})