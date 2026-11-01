(() => {
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  async function loadGitHubStatus() {
    const host = document.querySelector("main");
    if (!host) return;
    let panel = document.getElementById("github-live-status");
    if (!panel) {
      panel = document.createElement("section");
      panel.id = "github-live-status";
      panel.className = "section-card";
      panel.style.marginTop = "22px";
      panel.innerHTML = '<div class="section-head"><div><h3>اتصال GitHub المباشر</h3><p>بيانات مباشرة من GitHub REST API</p></div></div><p id="github-live-body">جارٍ جلب بيانات المستودع…</p>';
      host.appendChild(panel);
    }
    const body = panel.querySelector("#github-live-body");
    try {
      const response = await fetch("/api/github", {cache:"no-store", headers:{"Accept":"application/json"}});
      const data = await response.json();
      if (!response.ok || !data.connected) throw new Error(data.error || "GitHub API غير متاح");
      const run = data.latest_workflow
        ? esc(data.latest_workflow.name) + " — " + esc(data.latest_workflow.status) + " / " + esc(data.latest_workflow.conclusion || "قيد التنفيذ")
        : "لا توجد بيانات تشغيل Actions متاحة";
      body.innerHTML = '<div class="activity">' +
        '<div class="activity-row"><span>المستودع</span><b><a href="' + esc(data.html_url) + '" target="_blank" rel="noopener noreferrer">' + esc(data.repository) + '</a></b></div>' +
        '<div class="activity-row"><span>الفرع الافتراضي</span><b>' + esc(data.default_branch) + '</b></div>' +
        '<div class="activity-row"><span>آخر commit</span><b><a href="' + esc(data.latest_commit.html_url) + '" target="_blank" rel="noopener noreferrer">' + esc(data.latest_commit.short_sha) + '</a></b></div>' +
        '<div class="activity-row"><span>رسالة commit</span><b>' + esc(data.latest_commit.message) + '</b></div>' +
        '<div class="activity-row"><span>GitHub Actions</span><b>' + run + '</b></div>' +
        '<div class="activity-row"><span>مصدر البيانات</span><b>' + esc(data.source) + '</b></div></div>';
    } catch (error) {
      body.textContent = "تعذر جلب الحالة الحية من GitHub: " + error.message;
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", loadGitHubStatus, {once:true});
  else loadGitHubStatus();
  window.addEventListener("focus", loadGitHubStatus);
})();