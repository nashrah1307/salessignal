// frontend/src/pages/DealDetail.jsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchDeal, fetchCoach } from "../api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer, Cell } from "recharts";

export default function DealDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [detail, setDetail]  = useState(null);
  const [coach,  setCoach]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [coachLoading, setCoachLoading] = useState(true);

  useEffect(() => {
    fetchDeal(id).then(data => { setDetail(data); setLoading(false); });
    fetchCoach(id).then(data => { setCoach(data); setCoachLoading(false); });
  }, [id]);

  if (loading) return <p style={{padding:"24px", fontFamily:"Arial"}}>Loading deal...</p>;

  const shap = detail.shap_drivers.map(([feature, value]) => ({
    feature: feature.replace(/_/g, " "),
    value: value
  }));

  const prob = detail.probability;
  const probColor = prob < 35 ? "#E53935" : prob < 65 ? "#FB8C00" : "#43A047";

  return (
    <div style={{padding:"24px", fontFamily:"Arial", maxWidth:"900px"}}>
      <button onClick={() => navigate("/")}
        style={{marginBottom:"16px", padding:"6px 14px", background:"#1F4E79",
                color:"white", border:"none", borderRadius:"4px", cursor:"pointer"}}>
        ← Back to Pipeline
      </button>

      <h2 style={{color:"#1F4E79"}}>Deal {id}</h2>

      {/* Probability score */}
      <div style={{display:"flex", alignItems:"center", gap:"16px", margin:"16px 0",
                   padding:"16px", background:"#f5f5f5", borderRadius:"8px"}}>
        <div style={{fontSize:"48px", fontWeight:"bold", color: probColor}}>{prob}%</div>
        <div>
          <div style={{fontWeight:"bold", fontSize:"16px"}}>Close Probability</div>
          <div style={{color:"#666", fontSize:"13px"}}>
            {prob < 35 ? "High risk — needs immediate attention"
             : prob < 65 ? "Medium risk — monitor closely"
             : "On track — continue current approach"}
          </div>
        </div>
      </div>

      {/* Deal info */}
      <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap:"8px",
                   marginBottom:"24px", fontSize:"13px"}}>
        {[
          ["Product Line", detail.deal.product_line],
          ["Region", detail.deal.region],
          ["Deal Value", `$${Number(detail.deal.deal_value).toLocaleString()}`],
          ["Deal Size", detail.deal.deal_size_category],
          ["Days in Stage", detail.deal.days_in_stage],
          ["Stage Changes", detail.deal.stage_change_count],
          ["Competitor", detail.deal.competitor_type || "None"],
          ["Route To Market", detail.deal.route_to_market],
        ].map(([label, val]) => (
          <div key={label} style={{padding:"10px 12px", background:"#EBF3FB", borderRadius:"6px"}}>
            <span style={{color:"#666"}}>{label}: </span>
            <span style={{fontWeight:"bold", color:"#1F4E79"}}>{val}</span>
          </div>
        ))}
      </div>

      {/* SHAP chart */}
      <h3 style={{color:"#1F4E79", marginBottom:"8px"}}>Risk Drivers (SHAP)</h3>
      <p style={{color:"#666", fontSize:"13px", marginBottom:"12px"}}>
        Negative values = hurting the deal · Positive values = helping the deal
      </p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={shap} layout="vertical" margin={{left:20, right:40}}>
          <XAxis type="number" domain={["auto","auto"]} tick={{fontSize:12}}/>
          <YAxis type="category" dataKey="feature" tick={{fontSize:12}} width={140}/>
          <Tooltip />
          <ReferenceLine x={0} stroke="#666" />
          <Bar dataKey="value" radius={[0,4,4,0]}>
            {shap.map((entry, i) => (
              <Cell key={i} fill={entry.value < 0 ? "#E53935" : "#43A047"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Coach recommendation */}
      <h3 style={{color:"#1F4E79", margin:"24px 0 8px"}}>AI Coach Recommendation</h3>
      {coachLoading ? (
        <p style={{color:"#666"}}>Generating recommendation...</p>
      ) : (
        <div style={{background:"#EBF3FB", borderLeft:"4px solid #1F4E79",
                     padding:"16px", borderRadius:"0 8px 8px 0", fontSize:"13px",
                     lineHeight:"1.8", whiteSpace:"pre-wrap"}}>
          {coach?.recommendation || "No recommendation available"}
        </div>
      )}
    </div>
  );
}
