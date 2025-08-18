function showPage(page) {
  const pages = ["dashboard", "logs", "rules"];
  pages.forEach((p) => {
    const el = document.getElementById(p + "-page");
    el.style.display = p === page ? "block" : "none";
  });

  // Load data when page is shown
  if (page === "logs") fetchLogs();
  if (page === "rules") fetchRules();
}

// Initialize default page
showPage("dashboard");
