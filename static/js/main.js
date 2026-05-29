// main.js - SGRDMS

// Toggle sidebar
const toggleBtn    = document.getElementById("toggleSidebar");
const sidebar      = document.getElementById("sidebar");
const mainContent  = document.getElementById("mainContent");

if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
        mainContent.classList.toggle("collapsed");
    });
}

// Auto-fermer les alertes après 4 secondes
document.querySelectorAll(".alert").forEach(alert => {
    setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
    }, 4000);
});