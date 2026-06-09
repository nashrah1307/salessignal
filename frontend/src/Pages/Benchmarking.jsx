// frontend/src/pages/Benchmarking.jsx
import { useEffect, useState } from "react";
import { fetchBenchmarks } from "../api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function Benchmarking() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeType, setActiveType] = useState("product_line");

  useEffect(() => {
    fetchBenchmarks().then(d => { setData(d); setLoading(false); });
  }, []);

  if (loading) return <p style={{padding:"24px", fontFamily:"Arial"}}>Loading benchmarks...</p>;

  const types = ["product_line", "region", "deal_size_category", "route_to_market"];
  const filtered = data
    .filter(d => d.segment_type === activeType)
    .sort((a, b) => b.win_rate - a.win_rate);

  const chartData = filtered.map(d => ({
    name: d.segment_value,
    win_rate: Math.round(d.win_rate * 100),
    avg_days: Math.round(d.avg_days_closing)
  }));

  return (
    <div style={{padding:"24px", fontFamily:"Arial"}}>
      <h2 style={{color:"#1F4E79", marginBottom:"16px"}}>Segment Benchmarking</h2>

      <div style={{display:"flex", gap:"8px", marginBottom:"24px"}}>
        {types.map(t => (
          <button key={t} onClick={() => setActiveType(t)}
            style={{padding:"6px 14px", borderRadius:"4px", border:"none", cursor:"pointer",
                    background: activeType === t ? "#1F4E79" : "#e0e0e0",
                    color: activeType === t ? "white" : "#333",
                    fontWeight: activeType === t ? "bold" : "normal"}}>
            {t.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      <h3 style={{color:"#1F4E79", marginBottom:"8px"}}>Win Rate by {activeType.replace(/_/g, " ")}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{bottom:60}}>
          <XAxis dataKey="name" tick={{fontSize:11}} angle={-30} textAnchor="end" interval={0}/>
          <YAxis tickFormatter={v => `${v}%`} tick={{fontSize:12}}/>
          <Tooltip formatter={v => `${v}%`}/>
          <Bar dataKey="win_rate" radius={[4,4,0,0]}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.win_rate > 30 ? "#1F4E79" : "#E53935"}/>
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <h3 style={{color:"#1F4E79", margin:"32px 0 8px"}}>Avg Days to Close</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{bottom:60}}>
          <XAxis dataKey="name" tick={{fontSize:11}} angle={-30} textAnchor="end" interval={0}/>
          <YAxis tick={{fontSize:12}}/>
          <Tooltip/>
          <Bar dataKey="avg_days" fill="#2E75B6" radius={[4,4,0,0]}/>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
