
import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img
          src="/pl_predictor_logo.svg"
          alt="PL Predictor"
        />
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

      <div className="sidebar-footer">
        <NavLink
          to="/about"
          className={({ isActive }) =>
            `sidebar-about-link${isActive ? " active" : ""}`
          }
        >
          <span className="about-icon">ⓘ</span>
          <span>About Us</span>
          <span className="about-arrow">→</span>
        </NavLink>
      </div>
    </aside>
  );
}

export default Sidebar;
