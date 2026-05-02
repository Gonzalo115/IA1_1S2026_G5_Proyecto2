import "./Sidebar.css";

export type ActiveTab = "usuario" | "admin";

interface Props {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
}

const tabs: { id: ActiveTab; label: string; description: string }[] = [
  {
    id: "usuario",
    label: "Módulo de Usuario",
    description: "Detección en tiempo real",
  },
  {
    id: "admin",
    label: "Administrador",
    description: "Configuración, señas y entrenamiento",
  },
];

export default function Sidebar({ activeTab, onTabChange }: Props) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-logo">HT</div>
        <div className="brand-text">
          <p className="brand-name">HandTalk AI</p>
          <p className="brand-sub">Lenguaje de señas</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`nav-item ${activeTab === tab.id ? "nav-active" : ""}`}
            onClick={() => onTabChange(tab.id)}
          >
            <span className="nav-label">{tab.label}</span>
            <span className="nav-desc">{tab.description}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <p>Proyecto IA1</p>
        <p>Grupo 5 - 1S 2026</p>
      </div>
    </aside>
  );
}
