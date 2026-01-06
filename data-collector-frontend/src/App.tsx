import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import DataCollector from './components/DataCollector';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/data-collector" element={<DataCollector />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
