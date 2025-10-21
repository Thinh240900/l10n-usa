document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    const dropdown = document.getElementById("bankDropdown");

    if (!dropdown) return;

    const toggle = dropdown.querySelector(".bank-dropdown-toggle");
    const menu = dropdown.querySelector(".bank-dropdown-menu");

    toggle.addEventListener("click", function () {
        menu.classList.toggle("d-none");
    });

    menu.querySelectorAll(".bank-option").forEach((option) => {
        option.addEventListener("click", function () {
            const bankId = this.id;

            toggle.querySelector(".bank-info").innerHTML = this.innerHTML;
            menu.classList.add("d-none");

            fetch("/autopay-method/change", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": odoo.csrf_token,
                },
                body: JSON.stringify({bank_id: bankId}),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === "success") {
                        console.log("✅ Autopay method updated:", bankId);
                    } else {
                        console.warn("⚠️ Update failed:", data.error || data);
                    }
                })
                .catch((error) => {
                    console.error("Error updating autopay method:", error);
                });
        });
    });

    document.addEventListener("click", function (e) {
        if (!dropdown.contains(e.target)) {
            menu.classList.add("d-none");
        }
    });
});
