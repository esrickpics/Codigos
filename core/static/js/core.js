document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const collapseBtn = document.getElementById("sidebarCollapseBtn");
    const mobileBtn = document.getElementById("mobileMenuBtn");
    const sidebarBackdrop = document.getElementById("app-sidebar-backdrop");
    const SIDEBAR_STATE_KEY = "app.sidebar.collapsed";

    const isDesktop = () => window.innerWidth > 992;

    try {
        const savedCollapsed = localStorage.getItem(SIDEBAR_STATE_KEY) === "1";
        if (savedCollapsed && isDesktop()) {
            body.classList.add("app-sidebar-collapsed");
        }
    } catch (e) {
        // Ignore storage errors and continue with default state.
    }

    if (collapseBtn) {
        collapseBtn.addEventListener("click", () => {
            body.classList.toggle("app-sidebar-collapsed");
            try {
                localStorage.setItem(
                    SIDEBAR_STATE_KEY,
                    body.classList.contains("app-sidebar-collapsed") ? "1" : "0",
                );
            } catch (e) {
                // Ignore storage errors.
            }
        });
    }

    const toggleDrawer = () => {
        body.classList.toggle("sidebar-drawer-open");
    };

    if (mobileBtn) {
        mobileBtn.addEventListener("click", toggleDrawer);
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener("click", () => {
            body.classList.remove("sidebar-drawer-open");
        });
    }

    window.addEventListener("resize", () => {
        if (window.innerWidth > 992) {
            body.classList.remove("sidebar-drawer-open");
            try {
                const savedCollapsed = localStorage.getItem(SIDEBAR_STATE_KEY) === "1";
                body.classList.toggle("app-sidebar-collapsed", savedCollapsed);
            } catch (e) {
                // Ignore storage errors.
            }
        }
    });
});
