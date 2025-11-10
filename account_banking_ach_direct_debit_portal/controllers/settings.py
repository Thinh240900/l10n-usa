from odoo import fields, http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

from .user_portal import UserPortalController as user_portal


class SettingsController(CustomerPortal):
    @http.route(
        ["/my/settings"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def ach_settings(self, **kw):
        if not user_portal.is_ach_accessible():
            return user_portal.deny_403()

        partner = request.env.user.partner_id

        bank_accounts = request.env["res.partner.bank"].search(
            [("partner_id", "=", partner.id)],
        )

        today = fields.Date.today()
        Invoice = request.env["account.move"].sudo()
        PaymentToken = request.env["payment.token"].sudo()

        domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("partner_id", "=", partner.id),
            ("amount_residual", ">", 0),
            ("payment_state", "in", ["not_paid", "partial"]),
            ("invoice_date_due", ">=", today),
        ]

        next_due_invoice = Invoice.read_group(
            domain,
            fields=["invoice_date_due:min"],
            groupby=[]
        )
        next_due_date = next_due_invoice and next_due_invoice[0]["invoice_date_due"] or False

        credit_cards = PaymentToken.search(
            [
                ("partner_id", "=", partner.id),
                ("active", "=", True),
            ]
        )

        values = {
            "partner": partner,
            "bank_accounts": bank_accounts,
            "credit_cards": credit_cards,
            "next_due_date": next_due_date,
        }

        return request.render(
            "account_banking_ach_direct_debit_portal.ach_settings", values
        )
