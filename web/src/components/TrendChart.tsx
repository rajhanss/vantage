import React from 'react';
import {
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { Observation, TrendForecast } from '../types';

interface TrendChartProps {
  observations: Observation[];
  forecast?: TrendForecast | null;
  metricName?: string;
}

export const TrendChart: React.FC<TrendChartProps> = ({
  observations,
  forecast,
  metricName = 'Activity',
}) => {
  const chartData = React.useMemo(() => {
    const rows: Array<{
      date: string;
      historical?: number;
      forecast?: number;
      lower80?: number;
      upper80?: number;
      lower95?: number;
      upper95?: number;
    }> = [];

    const sorted = [...observations].sort(
      (a, b) => new Date(a.observed_at).getTime() - new Date(b.observed_at).getTime()
    );
    for (const obs of sorted) {
      const dateStr = obs.observed_at.split('T')[0];
      rows.push({
        date: dateStr,
        historical: Math.round(obs.metric_value * 10) / 10,
      });
    }

    if (rows.length > 0 && forecast && forecast.points.length > 0) {
      const lastHist = rows[rows.length - 1];
      lastHist.forecast = lastHist.historical;
      lastHist.lower80 = lastHist.historical;
      lastHist.upper80 = lastHist.historical;
      lastHist.lower95 = lastHist.historical;
      lastHist.upper95 = lastHist.historical;

      for (const pt of forecast.points) {
        rows.push({
          date: pt.date,
          forecast: pt.value,
          lower80: pt.lower_80,
          upper80: pt.upper_80,
          lower95: pt.lower_95,
          upper95: pt.upper_95,
        });
      }
    }

    return rows;
  }, [observations, forecast]);

  if (chartData.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-xs border border-vantage-800 rounded bg-vantage-950">
        No observations recorded for this entity
      </div>
    );
  }

  const forecastStartDate = forecast && forecast.points.length > 0 ? forecast.points[0].date : null;

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="ci95" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.12} />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.02} />
            </linearGradient>
            <linearGradient id="ci80" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.05} />
            </linearGradient>
            <linearGradient id="histFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#10b981" stopOpacity={0.0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#242a38" />
          <XAxis
            dataKey="date"
            stroke="#64748b"
            tick={{ fontSize: 10, fill: '#94a3b8' }}
            tickFormatter={(val) => val.slice(5)}
          />
          <YAxis
            stroke="#64748b"
            tick={{ fontSize: 10, fill: '#94a3b8' }}
            tickFormatter={(val) => (val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val)}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--vt-bg-surface)',
              borderColor: 'var(--vt-border-subtle)',
              borderRadius: '4px',
              fontSize: '11px',
              color: 'var(--vt-text-primary)',
            }}
          />

          {forecastStartDate && (
            <ReferenceLine
              x={forecastStartDate}
              stroke="#3b82f6"
              strokeDasharray="4 4"
              label={{
                value: 'Forecast horizon',
                position: 'top',
                fill: '#60a5fa',
                fontSize: 10,
              }}
            />
          )}

          <Area
            type="monotone"
            dataKey="upper95"
            stroke="none"
            fill="url(#ci95)"
            fillOpacity={1}
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="upper80"
            stroke="none"
            fill="url(#ci80)"
            fillOpacity={1}
            isAnimationActive={false}
          />

          <Area
            type="monotone"
            dataKey="historical"
            stroke="#10b981"
            strokeWidth={1.5}
            fill="url(#histFill)"
            name={`Observed ${metricName}`}
            dot={{ r: 2, fill: '#10b981' }}
          />

          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#3b82f6"
            strokeWidth={1.5}
            strokeDasharray="4 4"
            dot={false}
            name="Holt-Winters 30-day projection"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
