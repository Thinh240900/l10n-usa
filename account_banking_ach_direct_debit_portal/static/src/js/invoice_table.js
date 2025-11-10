import { whenReady } from "@odoo/owl";

whenReady(() => {
    const checkboxes = document.querySelectorAll(".invoice-checkbox");
    const payButton = document.querySelector(".pay-btn");
    const manageBankBtn = document.querySelector(".manage-bank-btn");

    const updateActionVisibility = () => {
        const anyChecked = Array.from(checkboxes).some((cb) => cb.checked);
        payButton?.classList.toggle("d-none", !anyChecked);
        manageBankBtn?.classList.toggle("d-none", anyChecked);
    };

    if (checkboxes.length && payButton) {
        checkboxes.forEach((cb) => cb.addEventListener("change", updateActionVisibility));
        updateActionVisibility();
        payButton.addEventListener("click", () => {
            const ids = [...document.querySelectorAll(".invoice-checkbox:checked")].map(cb => cb.value);
            if (ids.length) {
                const query = ids.map(id => `invoice=${encodeURIComponent(id)}`).join("&");
                window.location.href = `/select-payment-method?${query}`;
            }
        });
    }
});
