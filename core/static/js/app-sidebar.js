/**
 * Sidebar + drawer + estado colapsado (desktop).
 * Copiar este archivo y app-sidebar.css a otro proyecto; enlazar ambos y usar el mismo HTML base.
 *
 * Opcional: data-app-sidebar-config en <body> como JSON para sobreescribir:
 * { "storageKey": "mi.app.sidebar", "desktopMinPx": 992 }
 */
(function () {
    "use strict";

    var defaults = {
        collapsedClass: "app-sidebar-collapsed",
        drawerClass: "sidebar-drawer-open",
        storageKey: "app.sidebar.collapsed",
        desktopMinPx: 992,
        collapseBtnId: "sidebarCollapseBtn",
        mobileBtnId: "mobileMenuBtn",
        backdropId: "app-sidebar-backdrop",
    };

    function readConfig() {
        var cfg = Object.assign({}, defaults);
        try {
            var el = document.body;
            if (el && el.dataset && el.dataset.appSidebarConfig) {
                var parsed = JSON.parse(el.dataset.appSidebarConfig);
                Object.assign(cfg, parsed);
            }
        } catch (e) {
            /* ignorar JSON inválido */
        }
        return cfg;
    }

    function isDesktop(cfg) {
        return window.innerWidth > cfg.desktopMinPx;
    }

    document.addEventListener("DOMContentLoaded", function () {
        var cfg = readConfig();
        var body = document.body;
        var collapseBtn = document.getElementById(cfg.collapseBtnId);
        var mobileBtn = document.getElementById(cfg.mobileBtnId);
        var backdrop = document.getElementById(cfg.backdropId);

        try {
            if (localStorage.getItem(cfg.storageKey) === "1" && isDesktop(cfg)) {
                body.classList.add(cfg.collapsedClass);
            }
        } catch (e) {
            /* sin localStorage */
        }

        if (collapseBtn) {
            collapseBtn.addEventListener("click", function () {
                body.classList.toggle(cfg.collapsedClass);
                try {
                    localStorage.setItem(
                        cfg.storageKey,
                        body.classList.contains(cfg.collapsedClass) ? "1" : "0",
                    );
                } catch (err) {
                    /* ignorar */
                }
            });
        }

        function closeDrawer() {
            body.classList.remove(cfg.drawerClass);
        }

        function toggleDrawer() {
            body.classList.toggle(cfg.drawerClass);
        }

        if (mobileBtn) {
            mobileBtn.addEventListener("click", toggleDrawer);
        }
        if (backdrop) {
            backdrop.addEventListener("click", closeDrawer);
        }

        window.addEventListener("resize", function () {
            if (window.innerWidth > cfg.desktopMinPx) {
                closeDrawer();
                try {
                    var saved = localStorage.getItem(cfg.storageKey) === "1";
                    body.classList.toggle(cfg.collapsedClass, saved);
                } catch (err) {
                    /* ignorar */
                }
            }
        });
    });
})();
