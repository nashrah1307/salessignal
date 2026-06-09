// frontend/src/App.jsx
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import PipelineHealth  from "./Pages/PipelineHealth.jsx";
import DealDetail      from "./Pages/DealDetail.jsx";
import Benchmarking    from "./Pages/Benchmarking.jsx";
import RevenueForecast from "./Pages/RevenueForecast.jsx";
import Chat from "./Pages/Chat.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{display:"flex", gap:"24px", padding:"14px 28px",
                   borderBottom:"2px solid #1F4E79", fontFamily:"Arial",
                   background:"#1F4E79"}}>
        <Link to="/" style={{color:"white", textDecoration:"none", fontWeight:"bold"}}>Pipeline</Link>
        <Link to="/benchmarks" style={{color:"white", textDecoration:"none", fontWeight:"bold"}}>Benchmarks</Link>
        <Link to="/forecast" style={{color:"white", textDecoration:"none", fontWeight:"bold"}}>Forecast</Link>
        <Link to="/chat" style={{color:"white", textDecoration:"none", fontWeight:"bold"}}>AI Agent</Link>
      </nav>
      <Routes>
        <Route path="/"           element={<PipelineHealth />} />
        <Route path="/deal/:id"   element={<DealDetail />} />
        <Route path="/benchmarks" element={<Benchmarking />} />
        <Route path="/forecast"   element={<RevenueForecast />} />
        <Route path="/chat" element={<Chat />} />
      </Routes>
    </BrowserRouter>
  );
}
