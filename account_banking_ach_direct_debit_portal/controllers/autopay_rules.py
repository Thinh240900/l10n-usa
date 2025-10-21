import json
from datetime import date

from odoo import fields, http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

from ..controllers.user_portal import UserPortalController as user_portal


class AutoPayRulesController(CustomerPortal):
    @http.route(
        ["/autopay-rules"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def portal_autopay_rules(self, **kw):
        if not user_portal.is_ach_accessible():
            return user_portal.deny_403()

        if request.httprequest.method == "POST":
            autopay_rule = kw.get("autopay_rule")

            partner = request.env.user.partner_id
            partner.write({"autopay": autopay_rule})
            request.session["updated_autopay_rules"] = True
            return request.redirect("/autopay-rules")

        current_date = date.today().strftime("%-m-%-d-%Y")

        partner = request.env.user.partner_id

        bank_accounts = request.env["res.partner.bank"].search(
            [("partner_id", "=", partner.id)],
        )

        today = fields.Date.today()
        Invoice = request.env["account.move"].sudo()

        domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("partner_id", "=", partner.id),
            ("amount_residual", ">", 0),
            ("payment_state", "in", ["not_paid", "partial"]),
            ("invoice_date_due", ">=", today),
        ]

        next_due_invoice = Invoice.search(domain, order="invoice_date_due asc", limit=1)
        next_due_date = next_due_invoice.invoice_date_due if next_due_invoice else False

        values = {
            "page_name": "autopay_rules",
            "current_date": current_date,
            "partner": partner,
            "bank_accounts": bank_accounts,
            "next_due_date": next_due_date,
        }

        if request.session.get("updated_autopay_rules"):
            values["updated_autopay_rules"] = True
            request.session["updated_autopay_rules"] = False

        return request.render(
            "account_banking_ach_direct_debit_portal.portal_autopay_rules", values
        )

    # Frontend route: Handles the selection of an autopay rule when a user makes a choice
    @http.route(
        "/autopay-rules/change", type="http", auth="user", methods=["POST"], csrf=False
    )
    def update_autopay(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            autopay_value = data.get("autopay_rule")
        except Exception:
            return request.make_json_response({"error": "Invalid JSON"}, status=400)

        if autopay_value not in ["disabled", "specific_date", "on_due_date"]:
            return request.make_json_response({"error": "Invalid value"}, status=400)

        partner = request.env.user.partner_id
        partner.write({"autopay": autopay_value})

        if not partner.autopay_method and autopay_value != "disabled":
            bank = request.env["res.partner.bank"].search(
                [("partner_id", "=", partner.id)],
                order="default desc, id asc",
                limit=1,
            )

            if bank:
                partner.autopay_method = bank

        return request.make_json_response(
            {"status": "success", "autopay": autopay_value}
        )

    @http.route(
        "/autopay-method/change", type="http", auth="user", methods=["POST"], csrf=False
    )
    def update_autopay_method(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            bank_id = data.get("bank_id")
        except Exception:
            return request.make_json_response({"error": "Invalid JSON"}, status=400)

        partner = request.env.user.partner_id

        bank = request.env["res.partner.bank"].search(
            [
                ("id", "=", bank_id),
                ("partner_id", "=", partner.id),
            ],
            order="default desc, id asc",
            limit=1,
        )

        if bank:
            partner.autopay_method = bank

            return request.make_json_response({"status": "success", "bank_id": bank_id})

        return request.make_json_response({"error": "Bank not found"}, status=404)

    @http.route(
        "/autopay-specific-date/change",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def update_specific_date(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            date_str = data.get("specific_date")
        except Exception:
            return request.make_json_response({"error": "Invalid JSON"}, status=400)

        if not date_str:
            return request.make_json_response({"error": "Missing date"}, status=400)

        try:
            date_val = fields.Date.to_date(date_str)
        except Exception:
            return request.make_json_response({"error": "Invalid date"}, status=400)

        partner = request.env.user.partner_id

        if partner.autopay == "specific_date":
            partner.autopay_specific_date = date_val

            day = date_val.day
            return request.make_json_response({"status": "success", "day": day})

        return request.make_json_response(
            {"error": "Partner autopay is not specific date"}, status=400
        )
