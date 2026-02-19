import React, { useMemo } from 'react';
import { useVariables } from '../hooks/useVariableData';
import type { Variable } from '../types';

interface VariableListProps {
  selectedVariableId: string | null;
  onSelectVariable: (variableId: string) => void;
}

export const VariableList: React.FC<VariableListProps> = ({
  selectedVariableId,
  onSelectVariable,
}) => {
  const { data: variables, isLoading, isError } = useVariables();

  const groupedVariables = useMemo(() => {
    if (!variables) return {};
    
    return variables.reduce((acc, variable) => {
      if (!acc[variable.area]) {
        acc[variable.area] = [];
      }
      acc[variable.area].push(variable);
      return acc;
    }, {} as Record<string, Variable[]>);
  }, [variables]);

  const areaNames: Record<string, string> = {
    'pre-treatment': 'Pre-Treatment',
    'e-coat': 'E-Coat',
    'production-control': 'Production Control',
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-10 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="text-red-600">Error al cargar variables</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold text-gray-800">Variables</h2>
        <p className="text-sm text-gray-500">{variables?.length || 0} variables</p>
      </div>
      <div className="overflow-y-auto max-h-[600px]">
        {Object.entries(groupedVariables).map(([area, vars]) => (
          <div key={area} className="border-b last:border-b-0">
            <div className="bg-gray-50 px-4 py-2 font-medium text-gray-700 text-sm">
              {areaNames[area] || area} ({vars.length})
            </div>
            <div className="divide-y">
              {vars.map((variable) => (
                <button
                  key={variable.variable_id}
                  onClick={() => onSelectVariable(variable.variable_id)}
                  className={`w-full text-left px-4 py-2 hover:bg-gray-50 transition-colors ${
                    selectedVariableId === variable.variable_id
                      ? 'bg-blue-50 border-l-4 border-blue-500'
                      : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {variable.name}
                      </div>
                      <div className="text-xs text-gray-500">{variable.variable_id}</div>
                    </div>
                    <div className="ml-2 flex-shrink-0">
                      <span className="text-xs text-gray-500">{variable.unit}</span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
