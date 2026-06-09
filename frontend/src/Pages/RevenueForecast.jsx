// frontend/src/pages/RevenueForecast.jsx
import { useEffect, useState } from "react";
import { fetchAllDeals } from "../api";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";

export default function RevenueForecast() {
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    fetchAllDeals().then(deals => {
      const buckets = { "0-30": [0,0], "31-60": [0,0], "61-90": [0,0] };
      deals.forEach(d => {
        const days = d.total_days_closing || 0;
        const prob = (d.probability || 0) / 100;
        const val  = d.deal_value || 0;
        let bucket = null;
        if (days <= 30)       bucket = "0-30";
        else if (days <= 60)  bucket = "31-60";
        else if (days <= 90)  bucket = "61-90";
        if (bucket) {
          buckets[bucket][0] += val * prob;                        // conservative
          buckets[bucket][1] += prob > 0.5 ? val : val * prob;    // optimistic
        }
      });
      setForecast([
        { period: "0-30 days",  conservative: Math.round(buckets["0-30"][0]),  optimistic: Math.round(buckets["0-30"][1]) },
        { period: "31-60 days", conservative: Math.round(buckets["31-60"][0]), optimistic: Math.round(buckets["31-60"][1]) },
        { period: "61-90 days", conservative: Math.round(buckets["61-90"][0]), optimistic: Math.round(buckets["61-90"][1]) },
      ]);
      setLoading(false);
    });
  }, []);

  const fmt = (v) => `$${Number(v).toLocaleString()}`;

  if (loading) return <p style={{padding:"24px", fontFamily:"Arial"}}>Loading forecast...</p>;

  return (
    <div style={{padding:"24px", fontFamily:"Arial"}}>
      <h2 style={{color:"#1F4E79", marginBottom:"8px"}}>Revenue Forecast</h2>
      <p style={{color:"#666", fontSize:"13px", marginBottom:"24px"}}>
        Conservative = deal_value × probability · Optimistic = counts prob &gt; 50% as certain close
      </p>

      <ResponsiveContainer width="100%" height={350}>
        <AreaChart data={forecast}>
          <XAxis dataKey="period" tick={{fontSize:13}}/>
          <YAxis tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{fontSize:12}}/>
          <Tooltip formatter={fmt}/>
          <Legend/>
          <Area type="monotone" dataKey="optimistic"    stroke="#1F4E79" fill="#BDD7EE" name="Optimistic"/>
          <Area type="monotone" dataKey="conservative"  stroke="#43A047" fill="#C8E6C9" name="Conservative"/>
        </AreaChart>
      </ResponsiveContainer>

      <div style={{display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:"16px", marginTop:"32px"}}>
        {forecast.map(f => (
          <div key={f.period} style={{padding:"16px", background:"#EBF3FB",
                                      borderRadius:"8px", borderTop:"3px solid #1F4E79"}}>
            <div style={{fontWeight:"bold", color:"#1F4E79", marginBottom:"8px"}}>{f.period}</div>
            <div style={{fontSize:"13px", color:"#333"}}>Conservative: <strong>{fmt(f.conservative)}</strong></div>
            <div style={{fontSize:"13px", color:"#333"}}>Optimistic: <strong>{fmt(f.optimistic)}</strong></div>
          </div>
        ))}
      </div>
    </div>
  );
}
