import "@hotwired/turbo";
import Alpine from "alpinejs";
import "./preloader";
import "./style.css";

window.Alpine = Alpine;

const themeQuery = window.matchMedia("(prefers-color-scheme: dark)");

function getSavedTheme() {
    try {
        const saved = localStorage.getItem("theme");
        return ["light", "dark", "system"].includes(saved)
            ? saved
            : "system";
    } catch {
        return "system";
    }
}

function applyTheme(mode) {
    const isDark =
        mode === "dark" ||
        (mode === "system" && themeQuery.matches);

    document.documentElement.classList.toggle("dark", isDark);
    document.documentElement.style.colorScheme =
        isDark ? "dark" : "light";
}

Alpine.store("theme", {
    mode: getSavedTheme(),

    init() {
        applyTheme(this.mode);

        themeQuery.addEventListener("change", () => {
            if (this.mode === "system") {
                applyTheme("system");
            }
        });
    },

    set(mode) {
        if (!["light", "dark", "system"].includes(mode)) return;

        this.mode = mode;
        applyTheme(mode);

        try {
            localStorage.setItem("theme", mode);
        } catch {
            // Le thème fonctionne même sans stockage local.
        }
    },
});

Alpine.start();

