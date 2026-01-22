document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    // Function to initialize a dropdown
    function initializeDropdown(dropdownId) {
        const dropdown = document.getElementById(dropdownId);

        if (!dropdown) return;

        console.log(`[Dropdown] Initializing ${dropdownId}`);

        const toggle = dropdown.querySelector(".bank-dropdown-toggle");
        const menu = dropdown.querySelector(".bank-dropdown-menu");
        const hiddenInput = dropdown.querySelector("input[type='hidden']");

        if (!toggle || !menu || !hiddenInput) {
            console.log(`[Dropdown] Missing elements in ${dropdownId}`);
            return;
        }

        toggle.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            console.log(`[Dropdown] Toggle clicked for ${dropdownId}`);
            menu.classList.toggle("d-none");
        });

        const applySelectedFromValue = () => {
            const val = hiddenInput.value;
            menu.querySelectorAll(".bank-option").forEach((opt) => {
                opt.classList.toggle("selected", opt.id === val);
            });
        };
        applySelectedFromValue();

        menu.querySelectorAll(".bank-option").forEach((option) => {
            option.addEventListener("click", function (e) {
                e.stopPropagation();
                const selectedId = this.id;

                console.log(`[Dropdown] Option selected: ${selectedId}`);

                toggle.querySelector(".bank-info").innerHTML = this.innerHTML;
                const checkIcon = toggle.querySelector(".checkmark");
                if (checkIcon) checkIcon.remove();

                hiddenInput.value = selectedId;

                menu.classList.add("d-none");

                applySelectedFromValue();
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", function (e) {
            if (!dropdown.contains(e.target)) {
                menu.classList.add("d-none");
            }
        });

        console.log(`[Dropdown] ${dropdownId} initialized successfully`);
    }

    // Initialize both dropdowns
    initializeDropdown("bankPaymentDropdown");
    initializeDropdown("creditCardPaymentDropdown");
});
