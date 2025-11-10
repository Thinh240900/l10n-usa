(function () {
    "use strict";

    function initInvoiceTable() {
        console.log("[Invoice Table] Initializing...");

        const checkboxes = document.querySelectorAll(
            ".invoice-checkbox:not(:disabled)"
        );
        const allCheckboxes = document.querySelectorAll(".invoice-checkbox");
        const payButton = document.querySelector(".pay-btn");
        const manageBankBtn = document.querySelector(".manage-bank-btn");
        const selectAllCheckbox = document.getElementById("select-all-invoices");
        const selectAllOverdueCheckbox = document.getElementById("select-all-overdue");

        console.log("[Invoice Table] Found:", {
            checkboxes: checkboxes.length,
            payButton: Boolean(payButton),
            manageBankBtn: Boolean(manageBankBtn),
            selectAllCheckbox: Boolean(selectAllCheckbox),
            selectAllOverdueCheckbox: Boolean(selectAllOverdueCheckbox),
        });

        if (!checkboxes.length || !payButton) {
            console.log("[Invoice Table] Missing elements, skipping initialization");
            return;
        }

        const updateActionVisibility = () => {
            const anyChecked = Array.from(checkboxes).some((cb) => cb.checked);
            if (anyChecked) {
                payButton.classList.remove("d-none");
            } else {
                payButton.classList.add("d-none");
            }

            if (manageBankBtn) {
                if (anyChecked) {
                    manageBankBtn.classList.add("d-none");
                } else {
                    manageBankBtn.classList.remove("d-none");
                }
            }

            // Update select all checkbox state
            const selectAll = selectAllCheckbox || selectAllOverdueCheckbox;
            if (selectAll) {
                const allChecked = Array.from(checkboxes).every((cb) => cb.checked);
                const someChecked = Array.from(checkboxes).some((cb) => cb.checked);
                selectAll.checked = allChecked;
                selectAll.indeterminate = someChecked && !allChecked;
            }
        };

        // Select all checkbox handler
        const selectAll = selectAllCheckbox || selectAllOverdueCheckbox;
        if (selectAll) {
            selectAll.addEventListener("change", function () {
                console.log("[Invoice Table] Select all changed:", this.checked);
                checkboxes.forEach((cb) => {
                    cb.checked = this.checked;
                });
                updateActionVisibility();
            });
        }

        checkboxes.forEach((cb) => {
            cb.addEventListener("change", updateActionVisibility);
        });

        updateActionVisibility();

        console.log("[Invoice Table] Event listeners attached successfully");

        payButton.addEventListener("click", (e) => {
            e.preventDefault();
            console.log("[Invoice Table] Pay button clicked");

            const checkedBoxes = document.querySelectorAll(".invoice-checkbox:checked");
            const ids = Array.from(checkedBoxes).map((cb) => cb.value);

            console.log("[Invoice Table] Selected invoice IDs:", ids);

            if (ids.length) {
                const query = ids
                    .map((id) => `invoice=${encodeURIComponent(id)}`)
                    .join("&");
                const url = `/select-payment-method?${query}`;
                console.log("[Invoice Table] Redirecting to:", url);
                window.location.href = url;
            } else {
                console.log("[Invoice Table] No invoices selected");
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initInvoiceTable);
    } else {
        // DOM already loaded
        initInvoiceTable();
    }
})();
