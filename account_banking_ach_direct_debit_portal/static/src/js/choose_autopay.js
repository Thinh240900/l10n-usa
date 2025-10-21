document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    document.querySelectorAll(".option-card-input").forEach((radio) => {
        radio.addEventListener("click", function () {
            const autopayValue = this.value;

            const card = this.closest(".option-card");
            const extra = card.querySelector(".option-extra");

            document
                .querySelectorAll(".option-extra")
                .forEach((el) => el.classList.add("d-none"));

            if (extra) {
                extra.classList.remove("d-none");
            }

            fetch("/autopay-rules/change", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": odoo.csrf_token,
                },
                body: JSON.stringify({autopay_rule: autopayValue}),
            });
        });
    });
});
