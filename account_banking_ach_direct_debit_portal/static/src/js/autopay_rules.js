document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    const checkbox = document.getElementById("rule_disabled");

    if (checkbox) {
        checkbox.addEventListener("change", function (event) {
            const autopayValue = this.checked ? "on_due_date" : "disabled";
            const noBankAccounts = document.querySelector("[name='no_bank_accounts']");
            const warningSpan = document.getElementById("autopay-warning");

            if (noBankAccounts && noBankAccounts.value === "True" && this.checked) {
                event.preventDefault();
                this.checked = false;

                if (warningSpan) {
                    warningSpan.classList.remove("d-none");
                }
                return;
            }

            if (warningSpan) {
                warningSpan.classList.add("d-none");
            }

            fetch("/autopay-rules/change", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": odoo.csrf_token,
                },
                body: JSON.stringify({
                    autopay_rule: autopayValue,
                }),
            })
                .then((response) => response.json())
                .then(() => {
                    window.location.reload();
                })
                .catch((error) => {
                    console.error("Error:", error);
                });
        });
    }
});
