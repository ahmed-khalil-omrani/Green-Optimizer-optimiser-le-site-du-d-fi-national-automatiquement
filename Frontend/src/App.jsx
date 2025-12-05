import { Routes, Route } from 'react-router-dom';
import GreenOptimizer from './components/GreenOptimizer';
import MainPage from './components/MainPage';
import AnalysisReport from './components/AnalysisReport';
import './App.css';

function App() {
  return (
    <Routes>
      <Route path="/" element={<GreenOptimizer />}>
        <Route index element={<MainPage />} />
        <Route path="report" element={<AnalysisReport />} />
      </Route>
    </Routes>
  );
}

export default App;

