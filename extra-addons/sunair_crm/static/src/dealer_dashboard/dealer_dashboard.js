/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class DealerOverviewDashboard extends Component {
    static template = "dealer_dashboard.DealerOverview";

    setup() {
        this.orm    = useService("orm");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            period:  'all',
            kpis: {},
            territoryData:   [],
            productLineData: [],
            stateData:       [],
            appFunnel:       [],
            requestStates:   [],
            monthlyGrowth:   [],
            knowledgeDist:   [],
        });

        this.refs = {
            barChart:       useRef("barChart"),
            donutChart:     useRef("donutChart"),
            lineChart:      useRef("lineChart"),
            knowledgeChart: useRef("knowledgeChart"),
        };

        this.charts = {};

        onWillStart(async () => {
            await this._loadChartJS();
            await this._loadData();
        });

        onMounted(() => this._renderCharts());
    }

    async _loadChartJS() {
        if (window.Chart) return;
        await new Promise((res, rej) => {
            const s = document.createElement("script");
            s.src = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js";
            s.onload = res;
            s.onerror = () => rej(new Error("Chart.js load failed"));
            document.head.appendChild(s);
        });
    }

    async _loadData() {
        this.state.loading = true;
        try {
            const d = await this.orm.call("dealer.application", "get_dashboard_data", [this.state.period]);
            this.state.kpis            = d.kpis            || {};
            this.state.territoryData   = d.territory_data  || [];
            this.state.productLineData = d.product_line_data || [];
            this.state.stateData       = d.state_data      || [];
            this.state.appFunnel       = d.app_funnel      || [];
            this.state.requestStates   = d.request_states  || [];
            this.state.monthlyGrowth   = d.monthly_growth  || [];
            this.state.knowledgeDist   = d.knowledge_dist  || [];
        } catch (e) {
            console.error("Dealer dashboard load error:", e);
        } finally {
            this.state.loading = false;
        }
    }

    async setPeriod(period) {
        if (this.state.period === period) return;
        this.state.period = period;
        this._destroyCharts();
        await this._loadData();
        await new Promise(resolve => setTimeout(resolve, 50));
        this._renderCharts();
    }

    async onRefresh() {
        this._destroyCharts();
        await this._loadData();
        await new Promise(resolve => setTimeout(resolve, 50));
        this._renderCharts();
    }

    // ── Palette & tooltip ────────────────────────────────────
    _colors() {
        return ["#5B73F5","#10B5AD","#F5A623","#8B5CF6","#F5476A","#10B981","#E11D48","#0284C7"];
    }

    _tip() {
        return {
            backgroundColor: "rgba(15,26,46,.92)",
            titleColor:      "#F1F5F9",
            bodyColor:       "#8B9BB4",
            padding:         12,
            cornerRadius:    10,
            displayColors:   false,
        };
    }

    // ── Render ───────────────────────────────────────────────
    _renderCharts() {
        if (!window.Chart) return;
        this._renderBarChart();
        this._renderDonutChart();
        this._renderLineChart();
        this._renderKnowledgeChart();
    }

    _renderBarChart() {
        const el = this.refs.barChart.el;
        if (!el) return;
        const data   = this.state.territoryData.slice(0, 8);
        const colors = this._colors();
        this.charts.bar = new window.Chart(el.getContext("2d"), {
            type: "bar",
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    data:                data.map(d => d.count),
                    backgroundColor:     colors.slice(0, data.length).map(c => c + "BB"),
                    hoverBackgroundColor: colors.slice(0, data.length),
                    borderRadius:        8,
                    borderSkipped:       false,
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { ...this._tip(), callbacks: { label: ctx => ` ${ctx.parsed.y} dealers` } },
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: "rgba(15,26,46,.04)" }, ticks: { color: "#8B9BB4", font: { size: 11 } }, border: { display: false } },
                    x: { grid: { display: false }, ticks: { color: "#8B9BB4", font: { size: 11 }, maxRotation: 30 }, border: { display: false } },
                },
            },
        });
    }

    _renderDonutChart() {
        const el = this.refs.donutChart.el;
        if (!el) return;
        const data   = this.state.productLineData.slice(0, 7);
        const colors = this._colors();
        this.charts.donut = new window.Chart(el.getContext("2d"), {
            type: "doughnut",
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    data:            data.map(d => d.count),
                    backgroundColor: colors.slice(0, data.length),
                    borderWidth:     3,
                    borderColor:     "#FFFFFF",
                    hoverOffset:     8,
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                cutout: "64%",
                plugins: {
                    legend: {
                        position: "right",
                        labels: {
                            color: "#3B4A63", font: { size: 11.5 },
                            boxWidth: 10, boxHeight: 10, padding: 12,
                            usePointStyle: true, pointStyle: "rectRounded",
                        },
                    },
                    tooltip: this._tip(),
                },
            },
        });
    }

    _renderLineChart() {
        const el = this.refs.lineChart.el;
        if (!el) return;
        const data = this.state.monthlyGrowth;
        this.charts.line = new window.Chart(el.getContext("2d"), {
            type: "line",
            data: {
                labels: data.map(d => d.label),
                datasets: [{
                    data:                 data.map(d => d.count),
                    borderColor:          "#5B73F5",
                    backgroundColor:      "rgba(91,115,245,.07)",
                    tension:              0.42,
                    borderWidth:          2.5,
                    pointRadius:          5,
                    pointBackgroundColor: "#5B73F5",
                    pointBorderColor:     "#fff",
                    pointBorderWidth:     2,
                    pointHoverRadius:     7,
                    fill:                 true,
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: this._tip() },
                scales: {
                    y: { beginAtZero: true, grid: { color: "rgba(15,26,46,.04)" }, ticks: { color: "#8B9BB4", font: { size: 11 } }, border: { display: false } },
                    x: { grid: { display: false }, ticks: { color: "#8B9BB4", font: { size: 11 } }, border: { display: false } },
                },
            },
        });
    }

    _renderKnowledgeChart() {
        const el = this.refs.knowledgeChart.el;
        if (!el) return;
        const order   = ["Beginner","Basic","Intermediate","Advanced","Expert"];
        const palette = ["#E0E7FF","#A5B4FC","#6366F1","#4F46E5","#3730A3"];
        const sorted  = order.map(label => {
            const f = this.state.knowledgeDist.find(d => d.name === label);
            return f ? f.count : 0;
        });
        this.charts.knowledge = new window.Chart(el.getContext("2d"), {
            type: "bar",
            data: {
                labels: order,
                datasets: [{ data: sorted, backgroundColor: palette, borderRadius: 7, borderSkipped: false }],
            },
            options: {
                responsive: true, maintainAspectRatio: false, indexAxis: "y",
                plugins: {
                    legend: { display: false },
                    tooltip: { ...this._tip(), callbacks: { label: ctx => ` ${ctx.parsed.x} dealers` } },
                },
                scales: {
                    x: { beginAtZero: true, grid: { color: "rgba(15,26,46,.04)" }, ticks: { color: "#8B9BB4", font: { size: 11 } }, border: { display: false } },
                    y: { grid: { display: false }, ticks: { color: "#3B4A63", font: { size: 12, weight: "600" } }, border: { display: false } },
                },
            },
        });
    }

    _destroyCharts() {
        Object.keys(this.charts).forEach(k => {
            if (this.charts[k]) { this.charts[k].destroy(); this.charts[k] = null; }
        });
    }

    // ── Actions ──────────────────────────────────────────────
    actionViewAllDealers() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "All Dealers",
            res_model: "res.partner",
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            domain: [["is_dealer", "=", true]],
            target: "current",
        });
    }

    actionViewActiveDealers() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Active Dealers",
            res_model: "res.partner",
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            domain: [["is_dealer", "=", true], ["active", "=", true]],
            target: "current",
        });
    }

    actionViewNewThisMonth() {
        const startOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().slice(0, 10);
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "New Dealers This Month",
            res_model: "res.partner",
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            domain: [["is_dealer", "=", true], ["create_date", ">=", startOfMonth]],
            target: "current",
        });
    }

    actionViewApplications() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Dealer Applications",
            res_model: "dealer.application",
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            target: "current",
        });
    }

    actionViewRequests() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Dealer Requests",
            res_model: "dealer.request",
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            target: "current",
        });
    }

    // ── Helpers ──────────────────────────────────────────────
    getActivePercent() {
        const t = this.state.kpis.total_dealers;
        if (!t) return 0;
        return Math.round((this.state.kpis.active_dealers / t) * 100);
    }

    _maxOf(arr) { return Math.max(...arr.map(x => x.count), 1); }

    getStatusBarStyle(count) { return `width:${Math.round((count / this._maxOf(this.state.appFunnel)) * 100)}%`; }
    getReqBarStyle(count)    { return `width:${Math.round((count / this._maxOf(this.state.requestStates)) * 100)}%`; }
    getStateBarStyle(count)  { return `width:${Math.round((count / this._maxOf(this.state.stateData)) * 100)}%`; }
}

registry.category("actions").add("dealer_overview_dashboard", DealerOverviewDashboard);