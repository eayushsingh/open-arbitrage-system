import React, { useEffect, useRef } from 'react';
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, TimeScale } from 'chart.js';
import 'chartjs-adapter-luxon';

Chart.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, TimeScale);

export default function LiveChart({ data = [], labels = [], color = 'rgba(99,102,241,0.9)' }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    const ctx = canvasRef.current.getContext('2d');
    chartRef.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          data,
          borderColor: color,
          backgroundColor: 'rgba(99,102,241,0.14)',
          tension: 0.3,
          pointRadius: 0,
          borderWidth: 2,
        }]
      },
      options: {
        animation: { duration: 200 },
        scales: {
          x: { display: false },
          y: { display: true }
        },
        plugins: { legend: { display: false } },
        maintainAspectRatio: false
      }
    });

    return () => { chartRef.current && chartRef.current.destroy(); };
  }, []);

  useEffect(() => {
    if (!chartRef.current) return;
    chartRef.current.data.labels = labels;
    chartRef.current.data.datasets[0].data = data;
    chartRef.current.update('none');
  }, [data, labels]);

  return (
    <div className="live-chart">
      <canvas ref={canvasRef} />
    </div>
  );
}
