import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import JobList from './pages/JobList';
import JobSubmission from './pages/JobSubmission';
import JobDetail from './pages/JobDetail';

function App() {
  return (
    <Router>
      <Navbar />
      <div className="container mt-8">
        <Routes>
          <Route path="/" element={<JobList />} />
          <Route path="/jobs" element={<JobList />} />
          <Route path="/jobs/:id" element={<JobDetail />} />
          <Route path="/submit" element={<JobSubmission />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
