import React from 'react';

export default function MarketOverview({ markets }) {
  return (
    <div className="market-overview">
      {markets.map(m => (
        <div className="market-card" key={m.symbol}>
          <div className="m-left">
            <div className="m-symbol">{m.symbol}</div>
            <div className="m-price">{m.price}</div>
          </div>
          <div className="m-right">
            <div className={`m-spread ${m.spread>0? 'up': 'down'}`}>{m.spread.toFixed(2)}%</div>
          </div>
        </div>
      ))}
    </div>
  );
}
