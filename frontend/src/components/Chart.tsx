import {
  PieChart, Pie, Cell,
  BarChart, Bar,
  LineChart, Line,
  AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';

export type ChartType = 'pie' | 'bar' | 'line' | 'area';

interface ChartProps {
  type: ChartType;
  data: Record<string, unknown>[];
  dataKey?: string;
  nameKey?: string;
  xKey?: string;
  yKey?: string;
  colors?: string[];
  height?: number;
  showGrid?: boolean;
  showLegend?: boolean;
  showTooltip?: boolean;
  stacked?: boolean;
}

const DEFAULT_COLORS = [
  '#6366f1', '#22d3a5', '#f59e0b', '#f43f5e', '#818cf8',
  '#a78bfa', '#34d399', '#fbbf24', '#fb7185', '#60a5fa',
];

export default function Chart({
  type,
  data,
  dataKey = 'value',
  nameKey = 'name',
  xKey = 'name',
  yKey = 'value',
  colors = DEFAULT_COLORS,
  height = 300,
  showGrid = true,
  showLegend = true,
  showTooltip = true,
  stacked = false,
}: ChartProps) {
  const tooltipStyle = {
    contentStyle: {
      background: '#1c2333',
      border: '1px solid #252e45',
      borderRadius: '8px',
      fontSize: '13px',
    },
    itemStyle: { color: '#f1f5f9' },
    labelStyle: { color: '#94a3b8' },
  };

  const axisStyle = {
    tick: { fill: '#475569', fontSize: 12 },
    axisLine: { stroke: '#252e45' },
    tickLine: { stroke: '#252e45' },
  };

  if (type === 'pie') {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey={dataKey}
            nameKey={nameKey}
            stroke="none"
          >
            {data.map((_, i) => (
              <Cell key={i} fill={colors[i % colors.length]} />
            ))}
          </Pie>
          {showTooltip && <Tooltip {...tooltipStyle} />}
          {showLegend && (
            <Legend
              wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }}
              iconType="circle"
              iconSize={8}
            />
          )}
        </PieChart>
      </ResponsiveContainer>
    );
  }

  if (type === 'bar') {
    const barKeys = Object.keys(data[0] || {}).filter(k => k !== xKey);
    return (
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#252e45" />}
          <XAxis dataKey={xKey} {...axisStyle} />
          <YAxis {...axisStyle} />
          {showTooltip && <Tooltip {...tooltipStyle} />}
          {showLegend && <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />}
          {barKeys.map((key, i) => (
            <Bar
              key={key}
              dataKey={key}
              fill={colors[i % colors.length]}
              radius={[4, 4, 0, 0]}
              stackId={stacked ? 'stack' : undefined}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (type === 'area') {
    const areaKeys = Object.keys(data[0] || {}).filter(k => k !== xKey);
    return (
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#252e45" />}
          <XAxis dataKey={xKey} {...axisStyle} />
          <YAxis {...axisStyle} />
          {showTooltip && <Tooltip {...tooltipStyle} />}
          {showLegend && <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />}
          {areaKeys.map((key, i) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              fill={colors[i % colors.length]}
              stroke={colors[i % colors.length]}
              fillOpacity={0.1}
              stackId={stacked ? 'stack' : undefined}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    );
  }

  const lineKeys = Object.keys(data[0] || {}).filter(k => k !== xKey);
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#252e45" />}
        <XAxis dataKey={xKey} {...axisStyle} />
        <YAxis {...axisStyle} />
        {showTooltip && <Tooltip {...tooltipStyle} />}
        {showLegend && <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />}
        {lineKeys.map((key, i) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            stroke={colors[i % colors.length]}
            strokeWidth={2}
            dot={{ fill: colors[i % colors.length], r: 4 }}
            activeDot={{ r: 6 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
