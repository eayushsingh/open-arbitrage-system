import React from 'react';
import ConnectionIndicator from './ConnectionIndicator';

export default function Navbar({ connectionStatus, total }) {
  return (
    <header className="navbar">
      <div className="nav-left">
        <div className="logo">ArbiSaaS</div>
        <nav className="nav-links">
          <a>Dashboard</a>
          <a>Markets</a>
          <a>Trades</a>
        </nav>
      </div>

      <div className="nav-right">
        <div className="counter">Opportunities: <span>{total}</span></div>
        <ConnectionIndicator status={connectionStatus} />
        <div className="clock" id="live-clock" />
      </div>
    </header>
  );
}
