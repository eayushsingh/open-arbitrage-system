import React from 'react';

export default function ConnectionIndicator({ status }) {
  // status: connecting | open | closed | error | reconnecting
  const label = {
    connecting: 'Connecting',
    open: 'Live',
    closed: 'Closed',
    error: 'Error',
    reconnecting: 'Reconnecting'
  }[status] || 'Unknown';

  return (
    <div className={`conn ${status}`} title={`WebSocket: ${label}`}>
      <span className="dot" />
      <span className="label">{label}</span>
    </div>
  );
}
