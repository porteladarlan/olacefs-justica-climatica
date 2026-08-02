(function () {
    "use strict";

    const contrastStorageKey = "pjc:ui:high-contrast:v1";
    const supportedLanguages = new Set(["pt-br", "es", "en"]);

    const readContrastPreference = function () {
        try {
            return window.localStorage.getItem(contrastStorageKey) === "true";
        } catch (error) {
            return false;
        }
    };

    const writeContrastPreference = function (enabled) {
        try {
            window.localStorage.setItem(contrastStorageKey, String(enabled));
        } catch (error) {
            // Storage can be unavailable in privacy-restricted browsing contexts.
        }
    };

    const initializeContrast = function () {
        const button = document.getElementById("highContrastToggle");
        if (!button || button.dataset.initialized === "true") {
            return;
        }

        button.dataset.initialized = "true";

        const applyContrast = function (enabled, persist) {
            document.documentElement.classList.toggle("a11y-high-contrast", enabled);
            document.body.classList.toggle("a11y-high-contrast", enabled);
            button.setAttribute("aria-pressed", String(enabled));

            const label = enabled ? button.dataset.labelDisable : button.dataset.labelEnable;
            if (label) {
                button.setAttribute("aria-label", label);
                button.setAttribute("title", label);
            }

            if (persist) {
                writeContrastPreference(enabled);
            }
        };

        applyContrast(readContrastPreference(), false);
        button.addEventListener("click", function () {
            applyContrast(button.getAttribute("aria-pressed") !== "true", true);
        });
    };

    const initializeLanguageSwitcher = function () {
        const switcher = document.getElementById("languageSwitcher");
        if (!switcher || switcher.dataset.initialized === "true") {
            return;
        }

        switcher.dataset.initialized = "true";
        switcher.addEventListener("change", function () {
            const selectedLanguage = switcher.value;
            if (!supportedLanguages.has(selectedLanguage)) {
                return;
            }

            const currentUrl = new URL(window.location.href);
            let localizedPath = currentUrl.pathname.replace(/^\/(?:es|en)(?=\/|$)/, "") || "/";
            localizedPath = "/" + localizedPath.replace(/^\/+/, "");

            if (selectedLanguage === "es" || selectedLanguage === "en") {
                localizedPath = "/" + selectedLanguage + localizedPath;
            }

            const destination = new URL(localizedPath + currentUrl.search + currentUrl.hash, currentUrl.origin);
            if (destination.origin !== currentUrl.origin) {
                return;
            }
            window.location.assign(destination.href);
        });
    };

    const initializeMobileNavigation = function () {
        const menu = document.getElementById("menuPrincipal");
        const toggler = document.querySelector('[data-bs-target="#menuPrincipal"]');
        if (!menu || !toggler || menu.dataset.initialized === "true" || typeof bootstrap === "undefined") {
            return;
        }

        menu.dataset.initialized = "true";

        const isMobileMenu = function () {
            return window.matchMedia("(max-width: 991.98px)").matches;
        };

        const syncTogglerLabel = function (expanded) {
            const label = expanded ? toggler.dataset.labelClose : toggler.dataset.labelOpen;
            if (label) {
                toggler.setAttribute("aria-label", label);
            }
        };

        const hideMenu = function (restoreFocus) {
            if (!menu.classList.contains("show")) {
                return;
            }

            if (restoreFocus) {
                menu.addEventListener("hidden.bs.collapse", function () {
                    toggler.focus();
                }, { once: true });
            }

            bootstrap.Collapse.getOrCreateInstance(menu, { toggle: false }).hide();
        };

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && isMobileMenu()) {
                event.preventDefault();
                if (menu.classList.contains("collapsing") && !menu.classList.contains("show")) {
                    menu.addEventListener("shown.bs.collapse", function () {
                        hideMenu(true);
                    }, { once: true });
                } else {
                    hideMenu(true);
                }
            }
        });

        menu.addEventListener("click", function (event) {
            const link = event.target.closest("a[href]");
            if (link && isMobileMenu()) {
                hideMenu(false);
            }
        });

        document.addEventListener("click", function (event) {
            if (isMobileMenu() && !menu.contains(event.target) && !toggler.contains(event.target)) {
                hideMenu(false);
            }
        });

        menu.addEventListener("shown.bs.collapse", function () {
            syncTogglerLabel(true);
        });
        menu.addEventListener("hidden.bs.collapse", function () {
            syncTogglerLabel(false);
        });
        syncTogglerLabel(menu.classList.contains("show"));
    };

    const initializeShell = function () {
        initializeLanguageSwitcher();
        initializeContrast();
        initializeMobileNavigation();
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeShell, { once: true });
    } else {
        initializeShell();
    }
})();
