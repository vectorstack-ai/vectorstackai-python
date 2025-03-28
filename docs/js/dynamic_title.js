document.addEventListener("DOMContentLoaded", function () {
    // Default site title
    let siteTitle = "VectorStackAI";

    // Check if the URL contains "/precise_search/"
    if (window.location.pathname.includes("/precise_search/")) {
        siteTitle = "VectorStackAI | PreciseSearch";
    }

    // Check if the URL contains "/embeddings/"
    if (window.location.pathname.includes("/embeddings/")) {
        siteTitle = "VectorStackAI | Embeddings";
    }

    // Update the document title in the browser tab
    document.title = siteTitle;

    // Update the site title in the UI
    const titleElement = document.querySelector(".md-ellipsis");
    if (titleElement) {
        titleElement.textContent = siteTitle + " Documentation";  // Modify as needed
    }
});
