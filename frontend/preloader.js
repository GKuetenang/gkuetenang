let preloaderTimeout;
let initialPageLoaded = document.readyState === "complete";

function showPreloader() {
    clearTimeout(preloaderTimeout);

    preloaderTimeout = setTimeout(() => {
        document.documentElement.classList.add("page-loading");
    }, 200);
}

function hidePreloader() {
    clearTimeout(preloaderTimeout);
    document.documentElement.classList.remove("page-loading");
}

// Navigation Turbo
document.addEventListener("turbo:visit", showPreloader);

// Fin de navigation Turbo
document.addEventListener("turbo:load", () => {
    if (initialPageLoaded) {
        hidePreloader();
    }
});

// Éviter que l'overlay apparaisse dans une page mise en cache
document.addEventListener("turbo:before-cache", () => {
    document.documentElement.classList.remove("page-loading");
});

// Premier chargement complet (CSS, JS et autres ressources)
window.addEventListener("load", () => {
    initialPageLoaded = true;
    hidePreloader();
});

// Si le script arrive après l'événement load
if (document.readyState === "complete") {
    initialPageLoaded = true;
    hidePreloader();
}