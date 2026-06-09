// frontend/src/pages/PipelineHealth.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAllDeals } from "../api";

export default function PipelineHealth() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAllDeals().then(data => {
      const sorted = data.sort((a, b) => a.probability - b.probability);
      setDeals(sorted);
      setLoading(false);
    });
  }, []);

  function rowColor(prob) {
    if (prob < 35)  return "#FDECEA";
    if (prob < 65)  return "#FFF8E1";
    return "#E8F5E9";
  }

  function badge(prob) {
    if (prob < 35)  return { bg: "#E53935", label: "HIGH RISK" };
    if (prob < 65)  return { bg: "#FB8C00", label: "MEDIUM" };
    return { bg: "#43A047", label: "ON TRACK" };
  }

  if (loading) return <p style={{padding:"24px", fontFamily:"Arial"}}>Loading deals...</p>;

  return (
    <div style={{padding:"24px", fontFamily:"Arial"}}>
      <h2 style={{color:"#1F4E79", marginBottom:"16px"}}>Pipeline Health</h2>
      <p style={{color:"#555", marginBottom:"16px"}}>{deals.length} deals · sorted by risk (highest risk first)</p>
      <div style={{overflowX:"auto"}}>
        <table style={{width:"100%", borderCollapse:"collapse", fontSize:"13px"}}>
          <thead>
            <tr style={{background:"#1F4E79", color:"white"}}>
              <th style={{padding:"10px 12px", textAlign:"left"}}>Deal ID</th>
              <th style={{padding:"10px 12px", textAlign:"left"}}>Product Line</th>
              <th style={{padding:"10px 12px", textAlign:"left"}}>Region</th>
              <th style={{padding:"10px 12px", textAlign:"left"}}>Deal Size</th>
              <th style={{padding:"10px 12px", textAlign:"right"}}>Value (USD)</th>
              <th style={{padding:"10px 12px", textAlign:"right"}}>Days in Stage</th>
              <th style={{padding:"10px 12px", textAlign:"left"}}>Competitor</th>
              <th style={{padding:"10px 12px", textAlign:"center"}}>Probability</th>
              <th style={{padding:"10px 12px", textAlign:"center"}}>Risk</th>
            </tr>
          </thead>
          <tbody>
            {deals.map((d, i) => {
              const b = badge(d.probability);
              return (
                <tr key={i}
                  onClick={() => navigate(`/deal/${d.deal_id}`)}
                  style={{background: rowColor(d.probability), cursor:"pointer",
                          borderBottom:"1px solid #ddd"}}
                  onMouseEnter={e => e.currentTarget.style.opacity = "0.85"}
                  onMouseLeave={e => e.currentTarget.style.opacity = "1"}>
                  <td style={{padding:"9px 12px", fontWeight:"bold", color:"#1F4E79"}}>{d.deal_id}</td>
                  <td style={{padding:"9px 12px"}}>{d.product_line}</td>
                  <td style={{padding:"9px 12px"}}>{d.region}</td>
                  <td style={{padding:"9px 12px"}}>{d.deal_size_category}</td>
                  <td style={{padding:"9px 12px", textAlign:"right"}}>${Number(d.deal_value).toLocaleString()}</td>
                  <td style={{padding:"9px 12px", textAlign:"right"}}>{d.days_in_stage}</td>
                  <td style={{padding:"9px 12px"}}>{d.competitor_type || "None"}</td>
                  <td style={{padding:"9px 12px", textAlign:"center", fontWeight:"bold"}}>{d.probability}%</td>
                  <td style={{padding:"9px 12px", textAlign:"center"}}>
                    <span style={{background:b.bg, color:"white", padding:"3px 8px",
                                  borderRadius:"4px", fontSize:"11px", fontWeight:"bold"}}>
                      {b.label}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
