import { useState, useCallback, useEffect } from "react";
import "./App.css";
import Sidebar, { type ActiveTab } from "./components/Sidebar/Sidebar";
import UserModule from "./modules/user/UserModule";
import AdminModule from "./modules/admin/AdminModule";
import { getConfig } from "./api/admin";
import type { AdminConfig } from "./types";

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("usuario");
  const [config, setConfig] = useState<AdminConfig | null>(null);

  const loadConfig = useCallback(async () => {
    try {
      const data = await getConfig();
      setConfig(data);
    } catch {
      /* backend not yet running */
    }
  }, []);

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  return (
    <div className="app-shell">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="main-content">
        {activeTab === "usuario" && <UserModule config={config} />}
        {activeTab === "admin" && (
          <AdminModule config={config} onConfigChange={loadConfig} />
        )}
      </main>
    </div>
  );
}
