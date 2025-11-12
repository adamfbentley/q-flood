import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApiKey } from '../context/ApiKeyContext';
import { toast } from 'react-toastify';

const Navbar: React.FC = () => {
  const { apiKey, setApiKey } = useApiKey();
  const [localApiKey, setLocalApiKey] = useState<string>(apiKey);

  useEffect(() => {
    setLocalApiKey(apiKey);
  }, [apiKey]);

  const handleApiKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalApiKey(e.target.value);
  };

  const handleApiKeySubmit = () => {
    setApiKey(localApiKey);
    // CQ-005: Replaced alert() with react-toastify for better UX.
    toast.success('API Key updated!');
  };

  return (
    <nav className="bg-gray-800 p-4 shadow-md">
      <div className="container flex justify-between items-center">
        <Link to="/jobs" className="text-white text-xl font-bold">
          Quantum Flood Dashboard
        </Link>
        <div className="flex items-center space-x-4">
          <Link to="/jobs" className="text-gray-300 hover:text-white">
            Job List
          </Link>
          <Link to="/submit" className="text-gray-300 hover:text-white">
            Submit Job
          </Link>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              placeholder="Enter API Key"
              value={localApiKey}
              onChange={handleApiKeyChange}
              className="px-3 py-1 rounded-md bg-gray-700 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleApiKeySubmit}
              className="bg-blue-600 text-white px-3 py-1 rounded-md text-sm hover:bg-blue-700"
            >
              Set Key
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
