import React, { useState, useMemo } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { VariableList } from './components/VariableList';
import { VariableChart } from './components/VariableChart';
import { AlarmPanel } from './components/AlarmPanel';
import { StatisticsCard } from './components/StatisticsCard';
import { ConnectionStatus } from './components/ConnectionStatus';
import { useVariables } from './hooks/useVariableData';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function Dashboard() {
  const [selectedVariableId, setSelectedVariableId] = useState<string | null>(null);
  const { data: variables, isError, isSuccess } = useVariables();

  const selectedVariable = useMemo(() => {
    if (!variables || !selectedVariableId) return null;
    return variables.find((v) => v.variable_id === selectedVariableId) || null;
  }, [variables, selectedVariableId]);

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-red-600 text-white p-4 shadow-lg">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold">KIA Paint Shop - IoT Dashboard</h1>
          <ConnectionStatus isConnected={isSuccess} isError={isError} />
        </div>
      </header>
      <main className="container mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left sidebar - Variable list */}
          <div className="lg:col-span-1">
            <VariableList
              selectedVariableId={selectedVariableId}
              onSelectVariable={setSelectedVariableId}
            />
          </div>

          {/* Main content area */}
          <div className="lg:col-span-2 space-y-4">
            {/* Alarm panel */}
            <AlarmPanel />

            {/* Variable chart */}
            <VariableChart variable={selectedVariable} />

            {/* Statistics card */}
            <StatisticsCard
              variableId={selectedVariableId}
              unit={selectedVariable?.unit || ''}
            />
          </div>
        </div>
      </main>
      <footer className="bg-white border-t mt-8 py-4">
        <div className="container mx-auto text-center text-sm text-gray-500">
          KIA Paint Shop IoT Prototype - Auto-refresh cada 30 segundos
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
}

export default App;
