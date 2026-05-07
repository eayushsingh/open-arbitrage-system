import React, { useMemo } from 'react';
import clsx from 'clsx';

// Card showing buy/sell exchanges, prices, spread, and small charts.
export default function OpportunityCard({ item, highlight }) {
  const profitable = item.profit_percent > 0;
  const spread = Number(item.spread ?? 0);

  return (
    <div className={clsx('opp-card', profitable && 'profitable', highlight && 'highlight') }>
      <div className="opp-header">
        <div className="symbol">{item.symbol}</div>
        <div className="meta">{new Date(item.created_at).toLocaleTimeString()}</div>
      </div>

      <div className="opp-body">
        <div className="side buy">
          <div className="label">BUY</div>
          <div className="ex">{item.buy_exchange}</div>
          <div className="price">{item.buy_price}</div>
        </div>

        <div className="center">
          <div className="spread">
            <div className="spread-value">{spread.toFixed(2)}%</div>
            <div className="profit {animated}">{item.profit_percent.toFixed(2)}%</div>
            <div className="spread-bar">
              <div className="bar-inner" style={{ width: `${Math.min(100, Math.abs(spread))}%` }} />
            </div>
          </div>
        </div>

        <div className="side sell">
          <div className="label">SELL</div>
          <div className="ex">{item.sell_exchange}</div>
          <div className="price">{item.sell_price}</div>
        </div>
      </div>

      <div className="opp-footer">
        <div className="detail">Spread: <strong>{spread.toFixed(4)}</strong></div>
        <div className="detail">Profit %: <strong>{item.profit_percent.toFixed(4)}</strong></div>
      </div>
    </div>
  );
}
