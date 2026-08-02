(function () {
    "use strict";

    let opener = null;

    document.querySelectorAll("[data-dialog-target]").forEach(function (button) {
        button.addEventListener("click", function () {
            const dialog = document.getElementById(button.dataset.dialogTarget);
            if (dialog && typeof dialog.showModal === "function") {
                opener = button;
                dialog.showModal();
                const closeButton = dialog.querySelector("[data-dialog-close]");
                if (closeButton) {
                    closeButton.focus();
                }
            }
        });
    });

    document.querySelectorAll(".norm-dialog").forEach(function (dialog) {
        const closeButton = dialog.querySelector("[data-dialog-close]");
        if (closeButton) {
            closeButton.addEventListener("click", function () {
                dialog.close();
            });
        }

        dialog.addEventListener("click", function (event) {
            if (event.target === dialog) {
                dialog.close();
            }
        });

        dialog.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                event.preventDefault();
                dialog.close();
            }
        });

        dialog.addEventListener("close", function () {
            if (opener && opener.isConnected) {
                opener.focus();
            }
            opener = null;
        });
    });
})();
