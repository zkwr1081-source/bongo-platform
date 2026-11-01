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
      const headers = {"Content-Type": "application/json", "Accept": "application/json"};
      const token = byId("execution-token")?.value.trim();
      if (token) headers.Authorization = "Bearer " + token;
      const response = await fetch("/api/agents/run", {
        method: "POST",
        headers,
        body: JSON.stringify({goal, ...(agent_ids ? {agent_ids} : {})})
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.error || ("HTTP " + response.status));
      }
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
  function installExecutionTokenField() {
    const button = byId("run-agents");
    if (!button || byId("execution-token")) return;
    const label = document.createElement("label");
    label.htmlFor = "execution-token";
    label.textContent = "رمز تنفيذ المهام (اختياري محلياً؛ مطلوب عند ضبط NEXORA_EXECUTION_TOKEN)";
    label.style.display = "block";
    label.style.margin = "10px 0 6px";
    const input = document.createElement("input");
    input.id = "execution-token";
    input.type = "password";
    input.autocomplete = "off";
    input.spellcheck = false;
    input.placeholder = "أدخل الرمز محلياً — لا يتم حفظه";
    input.setAttribute("aria-label", label.textContent);
    input.style.cssText = "display:block;width:100%;margin:8px 0 14px;padding:12px;border:1px solid var(--line,#253149);border-radius:10px;background:#0b1321;color:var(--text,#edf3ff)";
    button.parentNode.insertBefore(label, button);
    button.parentNode.insertBefore(input, button);
  }

  document.addEventListener("DOMContentLoaded", () => {
    installExecutionTokenField();
    byId("run-agents")?.addEventListener("click", runAgents);
    byId("load-agents")?.addEventListener("click", loadAgents);
  });
})();
