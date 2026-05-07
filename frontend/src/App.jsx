import React, { useMemo, useState, useEffect } from 'react';
import useOpportunitiesSocket from './hooks/useOpportunitiesSocket';
import Navbar from './components/Navbar';
import Filters from './components/Filters';
import OpportunityCard from './components/OpportunityCard';
import MarketOverview from './components/MarketOverview';
import LiveChart from './components/LiveChart';
import './dashboard.css';

// Main Dashboard page
export default function App() {
  // Use production WebSocket URL when built for production, otherwise use local dev
  // Prefer an environment-provided WS URL (Vite: import.meta.env.VITE_WS_URL).
  // Fall back to the Render-hosted URL for production, and localhost for dev.
  const envUrl = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_WS_URL)
    ? import.meta.env.VITE_WS_URL
    : null;

  const defaultProd = 'wss://open-arbitrage-system.onrender.com/ws/opportunities';
  const defaultDev = 'ws://127.0.0.1:8000/ws/opportunities';

  const wsUrl = envUrl || (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.PROD ? defaultProd : defaultDev);

  const { data, status, lastMessageAt, reconnect } = useOpportunitiesSocket(wsUrl);

  const [filters, setFilters] = useState({
    profitableOnly: false,
    symbol: null,
    exchange: null,
    minSpread: 0,
    sortBy: 'spread_desc'
  });

  // derive symbols and exchanges
  const symbols = useMemo(() => Array.from(new Set((data || []).map(d => d.symbol).filter(Boolean))), [data]);
  const exchanges = useMemo(() => Array.from(new Set((data || []).flatMap(d => [d.buy_exchange, d.sell_exchange]).filter(Boolean))), [data]);

  // filtering
  const filtered = useMemo(() => {
    let list = Array.isArray(data) ? data : [];
    if (filters.profitableOnly) list = list.filter(i => Number(i.profit_percent) > 0);
    if (filters.symbol) list = list.filter(i => i.symbol === filters.symbol);
    if (filters.exchange) list = list.filter(i => i.buy_exchange === filters.exchange || i.sell_exchange === filters.exchange);
    if (filters.minSpread) list = list.filter(i => Math.abs(Number(i.spread)) >= filters.minSpread);

    if (filters.sortBy === 'spread_desc') list = list.sort((a,b) => Math.abs(b.spread) - Math.abs(a.spread));
    if (filters.sortBy === 'profit_desc') list = list.sort((a,b) => Number(b.profit_percent) - Number(a.profit_percent));
    if (filters.sortBy === 'latest') list = list.sort((a,b) => new Date(b.created_at) - new Date(a.created_at));

    return list;
  }, [data, filters]);

  // small market overview for BTC/ETH/SOL/XRP
  const markets = useMemo(() => {
    const coins = ['BTC', 'ETH', 'SOL', 'XRP'];
    return coins.map(s => {
      const found = (data || []).find(d => d.symbol?.startsWith(s));
      return {
        symbol: s,
        price: found ? found.buy_price : '—',
        spread: found ? Number(found.spread || 0) : 0
      };
    });
  }, [data]);

  // build micro-history for charts (naive: last N spread entries per symbol)
  const [history, setHistory] = useState({});
  useEffect(() => {
    if (!Array.isArray(data)) return;
    const now = Date.now();
    setHistory(prev => {
      const copy = { ...prev };
      data.forEach(item => {
        const key = item.symbol || 'unknown';
        const arr = copy[key] ? [...copy[key]] : [];
        arr.push({ t: now, v: Number(item.spread || 0) });
        // keep last 40
        copy[key] = arr.slice(-40);
      });
      return copy;
    });
  }, [data]);

  useEffect(() => {
    // live clock
    const clock = document.getElementById('live-clock');
    const i = setInterval(() => {
      if (clock) clock.textContent = new Date().toLocaleTimeString();
    }, 1000);
    return () => clearInterval(i);
  }, []);

  const best = filtered[0];

  return (
    <div className="dashboard-root">
      <Navbar connectionStatus={status} total={(data || []).length} />

      <main className="dashboard-main">
        <section className="left-col">
          <div className="panel">
            <h2>Market Overview</h2>
            <MarketOverview markets={markets} />
          </div>

          <div className="panel">
            <h2>Filters</h2>
            <Filters filters={filters} setFilters={setFilters} symbols={symbols} exchanges={exchanges} />
          </div>

          <div className="panel">
            <h2>Best Opportunity</h2>
            {best ? <OpportunityCard item={best} highlight /> : <div className="empty">No opportunities</div>}
          </div>
        </section>

        <section className="right-col">
          <div className="panel panel-wide">
            <div className="panel-head">
              <h2>Live Opportunities</h2>
              <div className="meta">Status: {status} • Last: {lastMessageAt ? new Date(lastMessageAt).toLocaleTimeString() : '—'}</div>
            </div>

            <div className="ops-grid">
              {filtered.length === 0 && <div className="empty">No matches</div>}
              {filtered.map(item => (
                <OpportunityCard key={item.id} item={item} highlight={best && item.id === best.id} />
              ))}
            </div>
          </div>

          <div className="panel">
            <h2>Live Spread Chart (Best Symbol)</h2>
            {best ? (
              <LiveChart
                data={history[best.symbol]?.map(p => p.v) || []}
                labels={history[best.symbol]?.map(p => new Date(p.t).toLocaleTimeString()) || []}
              />
            ) : <div className="empty">No data</div>}
          </div>
        </section>
      </main>

    </div>
  );
}