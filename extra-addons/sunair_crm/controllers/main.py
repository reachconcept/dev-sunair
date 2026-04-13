from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class DealerRequestController(http.Controller):

    @http.route(['/become-a-dealer', '/'], type='http', auth='public', website=True, sitemap=True)
    def dealer_form(self, **kwargs):
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
        error = {}
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

        state_id = False
        if post.get('state_id'):
            try:
                state_id = int(post['state_id'])
            except (ValueError, TypeError):
                state_id = False

        vals = {
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
            'is_distributor': bool(post.get('is_distributor')),
            'is_retail':      bool(post.get('is_retail')),
            'is_wholesale':   bool(post.get('is_wholesale')),
            'years_in_business': post.get('years_in_business', '').strip(),
            'has_showroom':      post.get('has_showroom', 'no'),
            'how_heard':         post.get('how_heard', '').strip(),
            'comments':          post.get('comments', '').strip(),
            'sells_retractable_awnings':    post.get('sells_retractable_awnings', 'no'),
            'retractable_awnings_supplier': post.get('retractable_awnings_supplier', '').strip(),
            'retractable_awnings_sales_pct': post.get('retractable_awnings_sales_pct', '0_10'),
            'sells_solar_screens':    post.get('sells_solar_screens', 'no'),
            'solar_screens_supplier': post.get('solar_screens_supplier', '').strip(),
            'solar_screens_sales_pct': post.get('solar_screens_sales_pct', '0_10'),
            'solar_screens_type':     post.get('solar_screens_type', 'exterior'),
            'sells_pergola_louvered':    post.get('sells_pergola_louvered', 'no'),
            'pergola_louvered_supplier': post.get('pergola_louvered_supplier', '').strip(),
            'pergola_louvered_sales_pct': post.get('pergola_louvered_sales_pct', '0_10'),
            'stage_id': request.env['dealer.application.state'].sudo().search([
                ('is_submitted', '=', True)
            ], limit=1).id,
        }

        request.env['dealer.request'].sudo().create([vals])
        return request.render('sunair_crm.dealer_request_success', {})


class DealerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'dealer_application_count' in counters:
            partner = request.env.user.partner_id
            values['dealer_application_count'] = (
                request.env['dealer.application'].sudo().search_count([
                    ('partner_id', '=', partner.id)
                ])
            )
        return values

    def _get_dealer_form_values(self, app):
        """Mevcut kaydın değerlerini form dict'ine çevirir."""
        return {
            'company_legal_name':    app.company_legal_name or '',
            'dba_name':              app.dba_name or '',
            'street':                app.street or '',
            'city':                  app.city or '',
            'state_id':              str(app.state_id.id) if app.state_id else '',
            'zip_code':              app.zip_code or '',
            'phone':                 app.phone or '',
            'fax':                   app.fax or '',
            'cell':                  app.cell or '',
            'email':                 app.email or '',
            'billing_street':        app.billing_street or '',
            'billing_city':          app.billing_city or '',
            'billing_state_id':      str(app.billing_state_id.id) if app.billing_state_id else '',
            'billing_zip':           app.billing_zip or '',
            'business_type':         app.business_type or '',
            'business_type_other':   app.business_type_other or '',
            'duns_number':           app.duns_number or '',
            'year_established':      app.year_established or '',
            'federal_id':            app.federal_id or '',
            'tax_status':            app.tax_status or 'taxable',
            'tax_exempt_number':     app.tax_exempt_number or '',
            'multi_jurisdiction_attached': app.multi_jurisdiction_attached,
            'principle_name_1':      app.principle_name_1 or '',
            'principle_title_1':     app.principle_title_1 or '',
            'principle_ssn_1':       app.principle_ssn_1 or '',
            'principle_address_1':   app.principle_address_1 or '',
            'principle_city_1':      app.principle_city_1 or '',
            'principle_state_id_1':  str(app.principle_state_id_1.id) if app.principle_state_id_1 else '',
            'principle_phone_1':     app.principle_phone_1 or '',
            'principle_name_2':      app.principle_name_2 or '',
            'principle_title_2':     app.principle_title_2 or '',
            'principle_ssn_2':       app.principle_ssn_2 or '',
            'principle_address_2':   app.principle_address_2 or '',
            'principle_city_2':      app.principle_city_2 or '',
            'principle_state_id_2':  str(app.principle_state_id_2.id) if app.principle_state_id_2 else '',
            'principle_phone_2':     app.principle_phone_2 or '',
            'bank_name':             app.bank_name or '',
            'bank_account_number':   app.bank_account_number or '',
            'bank_address':          app.bank_address or '',
            'bank_city':             app.bank_city or '',
            'bank_state_id':         str(app.bank_state_id.id) if app.bank_state_id else '',
            'bank_zip':              app.bank_zip or '',
            'trade_ref_1_name':      app.trade_ref_1_name or '',
            'trade_ref_1_phone':     app.trade_ref_1_phone or '',
            'trade_ref_1_fax':       app.trade_ref_1_fax or '',
            'trade_ref_1_address':   app.trade_ref_1_address or '',
            'trade_ref_2_name':      app.trade_ref_2_name or '',
            'trade_ref_2_phone':     app.trade_ref_2_phone or '',
            'trade_ref_2_fax':       app.trade_ref_2_fax or '',
            'trade_ref_2_address':   app.trade_ref_2_address or '',
            'trade_ref_3_name':      app.trade_ref_3_name or '',
            'trade_ref_3_phone':     app.trade_ref_3_phone or '',
            'trade_ref_3_fax':       app.trade_ref_3_fax or '',
            'trade_ref_3_address':   app.trade_ref_3_address or '',
            'has_other_business_names': app.has_other_business_names,
            'other_business_names':  app.other_business_names or '',
            'has_bankruptcy':        app.has_bankruptcy,
            'bankruptcy_dates':      app.bankruptcy_dates or '',
            'signed_by_name':        app.signed_by_name or '',
            'signed_by_title':       app.signed_by_title or '',
            'is_awcbn':              app.is_awcbn,
            'awcbn_number':          app.awcbn_number or '',
        }

    # ------------------------------------------------------------------
    # Ana route — varsa mevcut kaydı aç, yoksa yeni form
    # ------------------------------------------------------------------
    @http.route(
        ['/my/dealer-applications', '/my/dealer-applications/page/<int:page>'],
        type='http', auth='user', website=True,
    )
    def portal_dealer_list(self, page=1, **kw):
        partner = request.env.user.partner_id
        existing = request.env['dealer.application'].sudo().search([
            ('partner_id', '=', partner.id)
        ], limit=1)
        states = request.env['res.country.state'].sudo().search(
            [('country_id.code', '=', 'US')], order='name'
        )
        if existing:
            values = self._get_dealer_form_values(existing)
            return request.render('sunair_crm.portal_dealer_detail', {
                'application': existing,
                'states': states,
                'error': {},
                'values': values,
                'edit_app_id': existing.id,
                'page_name': 'dealer_application',
            })
        return request.render('sunair_crm.portal_dealer_detail', {
            'application': None,
            'states': states,
            'error': {},
            'values': {},
            'edit_app_id': None,
            'page_name': 'dealer_application',
        })

    # ------------------------------------------------------------------
    # /new → aynı sayfaya yönlendir
    # ------------------------------------------------------------------
    @http.route('/my/dealer-applications/new', type='http', auth='user', website=True)
    def portal_dealer_new(self, **kw):
        return request.redirect('/my/dealer-applications')

    # ------------------------------------------------------------------
    # Submit
    # ------------------------------------------------------------------
    @http.route(
        '/my/dealer-applications/submit',
        type='http', auth='user', website=True, methods=['POST'], csrf=True,
    )
    def portal_dealer_submit(self, **post):
        partner = request.env.user.partner_id
        states = request.env['res.country.state'].sudo().search(
            [('country_id.code', '=', 'US')], order='name'
        )

        error = {}
        for f in ['company_legal_name', 'street', 'city', 'state_id', 'zip_code', 'phone', 'email']:
            if not post.get(f, '').strip():
                error[f] = True
        if post.get('email') and '@' not in post['email']:
            error['email'] = True
        if post.get('year_established'):
            y = post['year_established']
            if not y.isdigit() or not (1900 <= int(y) <= 2100):
                error['year_established'] = True

        def _int(v):
            try:
                return int(v) if v else False
            except (ValueError, TypeError):
                return False

        edit_app_id = _int(post.get('edit_app_id'))
        existing = None
        if edit_app_id:
            existing = request.env['dealer.application'].sudo().search([
                ('id', '=', edit_app_id), ('partner_id', '=', partner.id),
            ], limit=1)

        if error:
            return request.render('sunair_crm.portal_dealer_detail', {
                'application': existing,
                'states': states,
                'error': error,
                'values': post,
                'edit_app_id': edit_app_id,
                'page_name': 'dealer_application',
            })

        vals = {
            'partner_id':                  partner.id,
            'company_legal_name':          post.get('company_legal_name', '').strip(),
            'dba_name':                    post.get('dba_name', '').strip(),
            'street':                      post.get('street', '').strip(),
            'city':                        post.get('city', '').strip(),
            'state_id':                    _int(post.get('state_id')),
            'zip_code':                    post.get('zip_code', '').strip(),
            'phone':                       post.get('phone', '').strip(),
            'fax':                         post.get('fax', '').strip(),
            'cell':                        post.get('cell', '').strip(),
            'email':                       post.get('email', '').strip(),
            'billing_street':              post.get('billing_street', '').strip(),
            'billing_city':                post.get('billing_city', '').strip(),
            'billing_state_id':            _int(post.get('billing_state_id')),
            'billing_zip':                 post.get('billing_zip', '').strip(),
            'business_type':               post.get('business_type') or False,
            'business_type_other':         post.get('business_type_other', '').strip(),
            'duns_number':                 post.get('duns_number', '').strip(),
            'year_established':            post.get('year_established', '').strip(),
            'federal_id':                  post.get('federal_id', '').strip(),
            'tax_status':                  post.get('tax_status', 'taxable'),
            'tax_exempt_number':           post.get('tax_exempt_number', '').strip(),
            'multi_jurisdiction_attached': bool(post.get('multi_jurisdiction_attached')),
            'principle_name_1':            post.get('principle_name_1', '').strip(),
            'principle_title_1':           post.get('principle_title_1', '').strip(),
            'principle_ssn_1':             post.get('principle_ssn_1', '').strip(),
            'principle_address_1':         post.get('principle_address_1', '').strip(),
            'principle_city_1':            post.get('principle_city_1', '').strip(),
            'principle_state_id_1':        _int(post.get('principle_state_id_1')),
            'principle_phone_1':           post.get('principle_phone_1', '').strip(),
            'principle_name_2':            post.get('principle_name_2', '').strip(),
            'principle_title_2':           post.get('principle_title_2', '').strip(),
            'principle_ssn_2':             post.get('principle_ssn_2', '').strip(),
            'principle_address_2':         post.get('principle_address_2', '').strip(),
            'principle_city_2':            post.get('principle_city_2', '').strip(),
            'principle_state_id_2':        _int(post.get('principle_state_id_2')),
            'principle_phone_2':           post.get('principle_phone_2', '').strip(),
            'bank_name':                   post.get('bank_name', '').strip(),
            'bank_account_number':         post.get('bank_account_number', '').strip(),
            'bank_address':                post.get('bank_address', '').strip(),
            'bank_city':                   post.get('bank_city', '').strip(),
            'bank_state_id':               _int(post.get('bank_state_id')),
            'bank_zip':                    post.get('bank_zip', '').strip(),
            'trade_ref_1_name':            post.get('trade_ref_1_name', '').strip(),
            'trade_ref_1_phone':           post.get('trade_ref_1_phone', '').strip(),
            'trade_ref_1_fax':             post.get('trade_ref_1_fax', '').strip(),
            'trade_ref_1_address':         post.get('trade_ref_1_address', '').strip(),
            'trade_ref_2_name':            post.get('trade_ref_2_name', '').strip(),
            'trade_ref_2_phone':           post.get('trade_ref_2_phone', '').strip(),
            'trade_ref_2_fax':             post.get('trade_ref_2_fax', '').strip(),
            'trade_ref_2_address':         post.get('trade_ref_2_address', '').strip(),
            'trade_ref_3_name':            post.get('trade_ref_3_name', '').strip(),
            'trade_ref_3_phone':           post.get('trade_ref_3_phone', '').strip(),
            'trade_ref_3_fax':             post.get('trade_ref_3_fax', '').strip(),
            'trade_ref_3_address':         post.get('trade_ref_3_address', '').strip(),
            'has_other_business_names':    bool(post.get('has_other_business_names')),
            'other_business_names':        post.get('other_business_names', '').strip(),
            'has_bankruptcy':              bool(post.get('has_bankruptcy')),
            'bankruptcy_dates':            post.get('bankruptcy_dates', '').strip(),
            'signed_by_name':              post.get('signed_by_name', '').strip(),
            'signed_by_title':             post.get('signed_by_title', '').strip(),
            'is_awcbn':                    bool(post.get('is_awcbn')),
            'awcbn_number':                post.get('awcbn_number', '').strip(),
        }

        try:
            if existing:
                vals.pop('partner_id', None)
                existing.write(vals)
            else:
                app = request.env['dealer.application'].sudo().create(vals)
                app.sudo().action_send_application()
        except Exception:
            return request.render('sunair_crm.portal_dealer_detail', {
                'application': existing,
                'states': states,
                'error': {'_global': True},
                'values': post,
                'edit_app_id': edit_app_id,
                'page_name': 'dealer_application',
            })

        return request.redirect('/my/dealer-applications/thank-you')

    # ------------------------------------------------------------------
    # Teşekkür
    # ------------------------------------------------------------------
    @http.route('/my/dealer-applications/thank-you', type='http', auth='user', website=True)
    def portal_dealer_thankyou(self, **kw):
        return request.render('sunair_crm.portal_dealer_thankyou', {
            'page_name': 'dealer_application',
        })