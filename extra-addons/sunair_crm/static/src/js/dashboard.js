/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class SunairDashboard extends Component {
    static template = "sunair_crm.dashboard";

    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            customerTypes: [],
            searchQuery: "",
            searchResults: [],
            searchPerformed: false
        });

        onWillStart(async () => {
            await this.loadCustomerTypes();
        });
    }

    async loadCustomerTypes() {
        try {
            const types = await this.orm.searchRead(
                "customer.type",
                [["active", "=", true]],
                ["name", "icon", "color", "sequence"],
                { order: "sequence, id" }
            );
            this.state.customerTypes = types || [];
        } catch (error) {
            this.notification.add("Error loading customer types", { type: "danger" });
        }
    }

    get leftTypes() {
        const types = this.state.customerTypes;
        const mid = Math.ceil(types.length / 2);
        return types.slice(0, mid);
    }

    get rightTypes() {
        const types = this.state.customerTypes;
        const mid = Math.ceil(types.length / 2);
        return types.slice(mid);
    }

    getCardColor(colorIndex) {
        const colors = {
            1: "#4361ee",
            2: "#2ecc71", 
            3: "#e74c3c",
            4: "#f39c12",
            5: "#9b59b6",
            6: "#1abc9c",
            7: "#e67e22",
            8: "#34495e"
        };
        return colors[colorIndex] || "#4361ee";
    }

    updateSearch(ev) {
        this.state.searchQuery = ev.target.value;
        if (this.state.searchQuery.length === 0) {
            this.clearSearch();
        }
    }

    handleKeyPress(ev) {
        if (ev.key === 'Enter') {
            this.searchLeads();
        }
    }

    async searchLeads() {
        if (!this.state.searchQuery || this.state.searchQuery.trim().length < 2) {
            this.notification.add("Please enter at least 2 characters to search", { type: "warning" });
            return;
        }

        this.state.searchPerformed = true;
        
        try {
            const domain = [
                "|", "|",
                ["name", "ilike", this.state.searchQuery],
                ["email_from", "ilike", this.state.searchQuery],
                ["phone", "ilike", this.state.searchQuery]
            ];
            
            const leads = await this.orm.searchRead(
                "crm.lead",
                domain,
                ["name", "email_from", "phone", "customer_type_id", "stage_id"],
                { limit: 50 }
            );
            
            this.state.searchResults = leads || [];
            
            if (this.state.searchResults.length === 0) {
                this.notification.add("No leads found matching your search", { type: "info" });
            }
        } catch (error) {
            this.notification.add("Error searching leads", { type: "danger" });
        }
    }

    clearSearch() {
        this.state.searchQuery = "";
        this.state.searchResults = [];
        this.state.searchPerformed = false;
    }

    openCustomerType(type) {
        if (!type || !type.id) return;
        
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: type.name,
            res_model: "crm.lead",
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            domain: [["customer_type_id", "=", type.id]],
            context: { 
                default_customer_type_id: type.id,
                search_default_customer_type_id: type.id
            },
        });
    }

    openLead(lead) {
        if (!lead || !lead.id) return;
        
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: lead.name,
            res_model: "crm.lead",
            res_id: lead.id,
            views: [[false, "form"]],
            view_mode: "form",
        });
    }

    openFindDealer() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Dealers",
            res_model: "res.partner",
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            domain: [["is_dealer", "=", true]],
            context: { 
                default_is_dealer: true,
                search_default_is_dealer: true
            },
        });
    }

    createLead() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "New Lead",
            res_model: "crm.lead",
            views: [[false, "form"]],
            view_mode: "form",
            target: "current",
            context: { 
                default_type: "lead",
                create: true
            }
        });
    }
}

registry.category("actions").add("sunair_crm.dashboard", SunairDashboard);