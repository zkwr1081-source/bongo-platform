(() => {
  const byId = id => document.getElementById(id);
  const pretty = value => JSON.stringify(value, null, 2);
  async function runAgents() {
    const goal = byId("agent-goal").value.trim();
    const output = byId("agent-results");
    if (!goal) { output.textContent = "اكتب المهمة أولاً."; return; }
    const raw = byId("agent-ids").value.trim();
    const agent_ids = raw ? raw.split(",").map(x => x.trim()).filter(Boolean) : undefined;
    const button = byId("run-agents");
    button.disabled = true;
    button.textContent = "جارٍ التنفيذ…";
    output.textContent = "يتم إرسال المهمة إلى الوكلاء المحددين…";
    try {
      const response = await fetch("/api/agents/run", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Accept": "application/json"},
        body: JSON.stringify({goal, ...(agent_ids ? {agent_ids} : {})})
      });
      const data = await response.json();
      output.textContent = pretty(data);
    } catch (error) {
      output.textContent = "تعذر الاتصال بخادم NEXORA: " + error.message;
    } finally {
      button.disabled = false;
      button.textContent = "تنفيذ المهمة";
    }
  }
  async function loadAgents() {
    const target = byId("agent-list");
    target.textContent = "جارٍ تحميل السجل…";
    try {
      const response = await fetch("/api/agents", {cache:"no-store"});
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || response.status);
      target.textContent = "عدد الوكلاء: " + data.count + "\n" +
        data.agents.map(a => a.agent_id + " — " + a.department + " — " + a.specialty).join("\n");
    } catch (error) { target.textContent = "تعذر تحميل السجل: " + error.message; }
  }
  document.addEventListener("DOMContentLoaded", () => {
    byId("run-agents")?.addEventListener("click", runAgents);
    byId("load-agents")?.addEventListener("click", loadAgents);
  });
})();
