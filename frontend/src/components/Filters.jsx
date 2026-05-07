import React, { useMemo } from 'react';

export default function Filters({ filters, setFilters, symbols, exchanges }) {
  const onChange = (k, v) => setFilters(prev => ({ ...prev, [k]: v }));

  return (
    <div className="filters">
      <div className="filter-item">
        <label>Profitable only</label>
        <input type="checkbox" checked={filters.profitableOnly} onChange={e => onChange('profitableOnly', e.target.checked)} />
      </div>

      <div className="filter-item">
        <label>Symbol</label>
        <select value={filters.symbol || ''} onChange={e => onChange('symbol', e.target.value || null)}>
          <option value="">All</option>
          {symbols.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="filter-item">
        <label>Exchange</label>
        <select value={filters.exchange || ''} onChange={e => onChange('exchange', e.target.value || null)}>
          <option value="">All</option>
          {exchanges.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="filter-item">
        <label>Min Spread %</label>
        <input type="range" min="0" max="10" step="0.1" value={filters.minSpread} onChange={e => onChange('minSpread', Number(e.target.value))} />
        <div className="range-value">{filters.minSpread}%</div>
      </div>

      <div className="filter-item">
        <label>Sort</label>
        <select value={filters.sortBy} onChange={e => onChange('sortBy', e.target.value)}>
          <option value="spread_desc">Highest Spread</option>
          <option value="profit_desc">Highest Profit %</option>
          <option value="latest">Latest</option>
        </select>
      </div>
    </div>
  );
}
