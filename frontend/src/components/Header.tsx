import { Link, useLocation } from 'react-router-dom';
import './Header.css';

export default function Header() {
  const location = useLocation();

  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/" className="header-logo">
          🏠 Real Estate LLM
        </Link>
        
        <nav className="header-nav">
          <Link 
            to="/data-collector" 
            className={`nav-link ${location.pathname === '/data-collector' ? 'active' : ''}`}
          >
            📊 Data Collector
          </Link>
          <Link 
            to="/chatbot" 
            className={`nav-link ${location.pathname === '/chatbot' ? 'active' : ''}`}
          >
            💬 Chatbot
          </Link>
          <Link 
            to="/properties" 
            className={`nav-link ${location.pathname === '/properties' ? 'active' : ''}`}
          >
            🏘️ Properties
          </Link>
        </nav>
      </div>
    </header>
  );
}
