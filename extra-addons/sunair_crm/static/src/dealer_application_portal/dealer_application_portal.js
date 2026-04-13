/* dealer_portal.js */
(function () {
    function init() {
        var form = document.getElementById('dp-form');
        if (!form) return;

        var panels = Array.prototype.slice.call(form.querySelectorAll('.dp-step-panel'));
        var dots   = Array.prototype.slice.call(document.querySelectorAll('.dp-stepper .dp-step'));
        var current = 0;

        function goTo(idx) {
            panels.forEach(function (p, i) {
                p.style.display = (i === idx) ? 'block' : 'none';
            });
            dots.forEach(function (d, i) {
                d.classList.remove('active', 'done');
                if (i < idx)  d.classList.add('done');
                if (i === idx) d.classList.add('active');
            });
            current = idx;
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        form.querySelectorAll('[data-dp-next]').forEach(function (btn) {
            btn.addEventListener('click', function () { goTo(current + 1); });
        });
        form.querySelectorAll('[data-dp-prev]').forEach(function (btn) {
            btn.addEventListener('click', function () { goTo(current - 1); });
        });

        goTo(0);

        function toggleByCheckbox(cbId, rowId) {
            var cb  = document.getElementById(cbId);
            var row = document.getElementById(rowId);
            if (!cb || !row) return;
            function upd() { row.style.display = cb.checked ? '' : 'none'; }
            cb.addEventListener('change', upd);
            upd();
        }
        function toggleBySelect(selId, rowId, val) {
            var sel = document.getElementById(selId);
            var row = document.getElementById(rowId);
            if (!sel || !row) return;
            function upd() { row.style.display = sel.value === val ? '' : 'none'; }
            sel.addEventListener('change', upd);
            upd();
        }
        function toggleByRadio(name, rowId, val) {
            var row = document.getElementById(rowId);
            if (!row) return;
            function upd() {
                var checked = form.querySelector('input[name="' + name + '"]:checked');
                row.style.display = (checked && checked.value === val) ? '' : 'none';
            }
            form.querySelectorAll('input[name="' + name + '"]').forEach(function (r) {
                r.addEventListener('change', upd);
            });
            upd();
        }

        toggleBySelect('dp_tax_status',                'dp-tax-exempt-row',  'tax_exempt');
        toggleByRadio('business_type',                  'dp-btype-other-row', 'other');
        toggleByCheckbox('dp_has_other_business_names', 'dp-other-names-row');
        toggleByCheckbox('dp_has_bankruptcy',           'dp-bankruptcy-row');
        toggleByCheckbox('dp_is_awcbn',                 'dp-awcbn-row');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();