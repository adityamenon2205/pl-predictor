import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h1>PL</h1>
        <span>PREDICTOR</span>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/" end>
          Overview
        </NavLink>

        <NavLink to="/teams">
          Teams
        </NavLink>

        <NavLink to="/predict">
          Predictor
        </NavLink>

        <NavLink to="/analytics">
          Analytics
        </NavLink>

        <NavLink to="/history">
          History
        </NavLink>
      </nav>
    </aside>
  );
}

export default Sidebar;