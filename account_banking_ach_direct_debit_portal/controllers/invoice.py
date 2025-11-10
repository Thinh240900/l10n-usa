from odoo import _, fields, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv import expression

from odoo.addons.account.controllers.portal import PortalAccount
from odoo.addons.portal.controllers.portal import pager as portal_pager

from ..controllers.homepage import HomepageController as homepage_portal
from ..controllers.user_portal import UserPortalController as user_portal
from ..utils import get_invoice_due_status


class InvoiceController(PortalAccount):
    def _get_status_searchbar_filters(self):
        return {
            "all": {"label": _("All"), "domain": []},
            "paid": {
                "label": _("Paid"),
                "domain": [
                    ("state", "=", "posted"),
                    ("payment_state", "in", ("paid", "in_payment")),
                ],
            },
            "waiting": {
                "label": _("Unpaid"),
                "domain": [
                    ("state", "=", "posted"),
                    ("payment_state", "not in", ("in_payment", "paid", "reversed")),
                ],
            },
        }

    def _prepare_my_invoices_values(
        self,
        page,
        date_begin,
        date_end,
        sortby,
        invoice_sortby=None,
        invoice_status=None,
        domain=None,
        url="/my/invoices",
    ):
        values = self._prepare_portal_layout_values()
        AccountInvoice = request.env["account.move"]

        invoice_searchbar_sortings = homepage_portal._get_invoice_searchbar_sortings()
        invoice_status_filters = homepage_portal._get_invoice_status_filters()

        invoice_status_domain = invoice_status_filters.get(invoice_status, {}).get(
            "domain", []
        )

        domain = expression.AND(
            [
                domain or [],
                self._get_invoices_domain(),
                invoice_status_domain,
            ]
        )

        if not invoice_sortby:
            invoice_sortby = "newest"

        if not invoice_status:
            invoice_status = "all"

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        values.update(
            {
                "date": date_begin,
                # content according to pager and archive selected
                # lambda function to get the invoices recordset
                # when the pager will be defined in the main method of a route
                "invoices": lambda pager_offset: (
                    AccountInvoice.search(
                        domain,
                        order="date desc" if invoice_sortby == "newest" else "date",
                        limit=self._items_per_page,
                        offset=pager_offset,
                    )
                    if AccountInvoice.has_access("read")
                    else AccountInvoice
                ),
                "page_name": "invoice",
                "pager": {  # vals to define the pager.
                    "url": url,
                    "url_args": {
                        "date_begin": date_begin,
                        "date_end": date_end,
                        "sortby": sortby,
                    },
                    "total": AccountInvoice.search_count(domain)
                    if AccountInvoice.has_access("read")
                    else 0,
                    "page": page,
                    "step": self._items_per_page,
                },
                "default_url": url,
                "sortby": sortby,
                "invoice_searchbar_sortings": invoice_searchbar_sortings,
                "invoice_status_filters": invoice_status_filters,
                "invoice_sortby": invoice_sortby,
                "invoice_status": invoice_status,
            }
        )
        return values

    @http.route(
        ["/my/invoices", "/my/invoices/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_invoices(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        invoice_sortby=None,
        invoice_status=None,
        search="",
        search_in="all",
        **kw,
    ):
        searchbar_inputs = {
            "all": {"label": _("All"), "input": "all"},
            "name": {"label": _("Invoice"), "input": "name"},
            "partner": {"label": _("Partner"), "input": "partner_id"},
        }

        partner = request.env.user.partner_id

        domain = [("partner_id", "=", partner.id)]
        if search:
            if search_in == "name":
                domain += [("name", "ilike", search)]
            elif search_in == "partner":
                domain += [("partner_id.name", "ilike", search)]
            else:
                domain += [
                    "|",
                    ("name", "ilike", search),
                    ("partner_id.name", "ilike", search),
                ]

        values = self._prepare_my_invoices_values(
            page, date_begin, date_end, sortby, invoice_sortby, invoice_status, domain
        )

        # pager
        pager = portal_pager(**values["pager"])

        # content according to pager and archive selected
        invoices = values["invoices"](pager["offset"])
        request.session["my_invoices_history"] = invoices.ids[:100]

        invoice_due_status_values = get_invoice_due_status(invoices)

        values.update(
            {
                "invoices": invoices,
                "invoice_due_status_values": invoice_due_status_values,
                "pager": pager,
                "search": search,
                "search_in": search_in,
                "searchbar_inputs": searchbar_inputs,
                "invisible_button": not user_portal.is_ach_accessible(),
            }
        )

        return request.render(
            "account_banking_ach_direct_debit_portal.portal_custom_my_invoices", values
        )

    @http.route(
        ["/my/invoices/overdue", "/my/invoices/overdue/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_overdue_invoices(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        invoice_sortby=None,
        search="",
        search_in="all",
        **kw,
    ):
        searchbar_inputs = {
            "all": {"label": _("All"), "input": "all"},
            "name": {"label": _("Invoice"), "input": "name"},
            "partner": {"label": _("Partner"), "input": "partner_id"},
        }

        partner = request.env.user.partner_id
        today = fields.Date.today()

        # Domain for overdue invoices only
        domain = [
            ("partner_id", "=", partner.id),
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("payment_state", "not in", ("paid", "in_payment", "reversed")),
            ("invoice_date_due", "<", today),
            ("amount_residual", ">", 0.0),
        ]

        if search:
            if search_in == "name":
                domain += [("name", "ilike", search)]
            elif search_in == "partner":
                domain += [("partner_id.name", "ilike", search)]
            else:
                domain += [
                    "|",
                    ("name", "ilike", search),
                    ("partner_id.name", "ilike", search),
                ]

        # Force "awaiting_payment" status for overdue
        invoice_status = "awaiting_payment"

        values = self._prepare_my_invoices_values(
            page,
            date_begin,
            date_end,
            sortby,
            invoice_sortby,
            invoice_status,
            domain,
            url="/my/invoices/overdue",
        )

        # pager
        pager = portal_pager(**values["pager"])

        # content according to pager and archive selected
        invoices = values["invoices"](pager["offset"])
        request.session["my_invoices_history"] = invoices.ids[:100]

        invoice_due_status_values = get_invoice_due_status(invoices)

        # Calculate total overdue amount
        total_overdue_amount = sum(invoices.mapped("amount_residual"))

        values.update(
            {
                "invoices": invoices,
                "invoice_due_status_values": invoice_due_status_values,
                "pager": pager,
                "search": search,
                "search_in": search_in,
                "searchbar_inputs": searchbar_inputs,
                "invisible_button": not user_portal.is_ach_accessible(),
                "total_overdue_amount": total_overdue_amount,
                "overdue_count": len(invoices),
                "page_title": "Overdue Invoices",
            }
        )

        return request.render(
            "account_banking_ach_direct_debit_portal.portal_overdue_invoices", values
        )

    def _invoice_get_page_view_values(self, invoice, access_token, **kwargs):
        values = super()._invoice_get_page_view_values(invoice, access_token, **kwargs)

        invoice_due_status_value = get_invoice_due_status(invoice)[invoice.id]

        values["invoice_due_status_value"] = invoice_due_status_value

        payment_date = False

        if invoice.payment_state in ("paid", "in_payment"):
            dates = invoice.payment_ids.mapped("date")

            payment_date = max(dates) if dates else False

        values["payment_date"] = payment_date

        return values

    @http.route(
        ["/my/invoices/<int:invoice_id>"], type="http", auth="public", website=True
    )
    def portal_my_invoice_detail(
        self, invoice_id, access_token=None, report_type=None, download=False, **kw
    ):
        try:
            invoice_sudo = self._document_check_access(
                "account.move", invoice_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        if report_type in ("html", "pdf", "text"):
            return self._show_report(
                model=invoice_sudo,
                report_type=report_type,
                report_ref="account.account_invoices",
                download=download,
            )

        values = self._invoice_get_page_view_values(invoice_sudo, access_token, **kw)

        return request.render(
            "account_banking_ach_direct_debit_portal.ach_portal_invoice_page", values
        )
