import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import DataCollector from './components/DataCollector';
import Chatbot from './components/Chatbot';
import PropertyList from './components/PropertyList';
import BatchProcessing from './components/BatchProcessing';
import GoogleSheetsIntegration from './components/GoogleSheetsIntegration';
import Header from './components/Header';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/data-collector" element={<DataCollector />} />
          <Route path="/batch-processing" element={<BatchProcessing />} />
          <Route path="/google-sheets" element={<GoogleSheetsIntegration />} />
          <Route path="/chatbot" element={<Chatbot />} />
          <Route path="/properties" element={<PropertyList />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
