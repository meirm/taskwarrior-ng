/**
 * React Hooks for MCPO Client Integration
 * 
 * Provides React hooks for easy integration with the MCPO client,
 * including automatic state management, error handling, and loading states.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { MCPOClient, mcpoClient } from '@/services/mcpo-client';
import type {
  Task,
  CreateTaskRequest,
  ModifyTaskRequest,
  ListTasksRequest,
  ApiResponse,
} from '@/types/task';

/**
 * Hook State Interface
 */
interface UseMCPOState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

/**
 * Hook Actions Interface
 */
interface UseMCPOActions {
  reset: () => void;
  setData: (data: any) => void;
  setError: (error: Error | null) => void;
  setLoading: (loading: boolean) => void;
}

/**
 * Generic MCPO Hook Return Type
 */
type UseMCPOReturn<T, TArgs extends any[] = any[]> = UseMCPOState<T> & {
  execute: (...args: TArgs) => Promise<T>;
  reset: () => void;
};

/**
 * Base hook for MCPO operations
 */
function useBaseMCPO<T, TArgs extends any[] = any[]>(
  operation: (...args: TArgs) => Promise<T>,
  dependencies: React.DependencyList = []
): UseMCPOReturn<T, TArgs> {
  const [state, setState] = useState<UseMCPOState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const mountedRef = useRef(true);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const execute = useCallback(async (...args: TArgs): Promise<T> => {
    setState({ data: null, loading: true, error: null });

    try {
      const result = await operation(...args);
      
      if (mountedRef.current) {
        setState({ data: result, loading: false, error: null });
      }
      
      return result;
    } catch (error) {
      const errorObj = error instanceof Error ? error : new Error('Unknown error occurred');
      
      if (mountedRef.current) {
        setState({ data: null, loading: false, error: errorObj });
      }
      
      throw errorObj;
    }
  }, dependencies);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

/**
 * Hook for listing tasks
 */
export function useListTasks(autoLoad = false, params: ListTasksRequest = {}) {
  const hook = useBaseMCPO(
    () => mcpoClient.listTasks(params),
    [JSON.stringify(params)]
  );

  useEffect(() => {
    if (autoLoad) {
      hook.execute();
    }
  }, [autoLoad, JSON.stringify(params)]);

  return hook;
}

/**
 * Hook for adding a task
 */
export function useAddTask() {
  return useBaseMCPO(
    (params: CreateTaskRequest) => mcpoClient.addTask(params),
    []
  );
}

/**
 * Hook for modifying a task
 */
export function useModifyTask() {
  return useBaseMCPO(
    (params: ModifyTaskRequest) => mcpoClient.modifyTask(params),
    []
  );
}

/**
 * Hook for completing a task
 */
export function useCompleteTask() {
  return useBaseMCPO(
    (taskId: number | string) => mcpoClient.completeTask(taskId),
    []
  );
}

/**
 * Hook for uncompleting a task
 */
export function useUncompleteTask() {
  return useBaseMCPO(
    (taskId: number | string, uuid?: string) => mcpoClient.uncompleteTask(taskId, uuid),
    []
  );
}

/**
 * Hook for deleting a task
 */
export function useDeleteTask() {
  return useBaseMCPO(
    (taskId: number | string) => mcpoClient.deleteTask(taskId),
    []
  );
}

/**
 * Hook for starting a task
 */
export function useStartTask() {
  return useBaseMCPO(
    (taskId: number | string) => mcpoClient.startTask(taskId),
    []
  );
}

/**
 * Hook for stopping a task
 */
export function useStopTask() {
  return useBaseMCPO(
    (taskId: number | string) => mcpoClient.stopTask(taskId),
    []
  );
}

/**
 * Hook for batch operations
 */
export function useBatchCompleteTasks() {
  return useBaseMCPO(
    (taskIds: (number | string)[]) => mcpoClient.batchCompleteTasks(taskIds),
    []
  );
}

/**
 * Hook for getting projects
 */
export function useProjects(autoLoad = false) {
  const hook = useBaseMCPO(
    () => mcpoClient.getProjects(),
    []
  );

  useEffect(() => {
    if (autoLoad) {
      hook.execute();
    }
  }, [autoLoad]);

  return hook;
}

/**
 * Hook for getting tags
 */
export function useTags(autoLoad = false) {
  const hook = useBaseMCPO(
    () => mcpoClient.getTags(),
    []
  );

  useEffect(() => {
    if (autoLoad) {
      hook.execute();
    }
  }, [autoLoad]);

  return hook;
}

/**
 * Hook for getting summary
 */
export function useSummary(autoLoad = false) {
  const hook = useBaseMCPO(
    () => mcpoClient.getSummary(),
    []
  );

  useEffect(() => {
    if (autoLoad) {
      hook.execute();
    }
  }, [autoLoad]);

  return hook;
}

/**
 * Hook for purging tasks
 */
export function usePurgeTasks() {
  return useBaseMCPO(
    () => mcpoClient.purgeTasks(),
    []
  );
}

/**
 * Hook for direct tool invocation
 */
export function useMCPOTool<TArgs = any, TResult = any>(toolName: string) {
  return useBaseMCPO(
    (args?: TArgs) => mcpoClient.invokeTool<TArgs, TResult>(toolName, args),
    [toolName]
  );
}

/**
 * Hook for MCPO server info
 */
export function useMCPOServerInfo(autoLoad = false) {
  const hook = useBaseMCPO(
    () => mcpoClient.getServerInfo(),
    []
  );

  useEffect(() => {
    if (autoLoad) {
      hook.execute();
    }
  }, [autoLoad]);

  return hook;
}

/**
 * Hook for listing available tools
 */
export function useMCPOTools(autoLoad = false) {
  const hook = useBaseMCPO(
    () => mcpoClient.listTools(),
    []
  );

  useEffect(() => {
    if (autoLoad) {
      hook.execute();
    }
  }, [autoLoad]);

  return hook;
}

/**
 * Context Provider for MCPO Client
 * 
 * Provides a shared MCPO client instance across the application
 */
import React, { createContext, useContext, useMemo } from 'react';

interface MCPOContextValue {
  client: MCPOClient;
}

const MCPOContext = createContext<MCPOContextValue | undefined>(undefined);

export interface MCPOProviderProps {
  children: React.ReactNode;
  client?: MCPOClient;
  config?: {
    baseURL?: string;
    apiKey?: string;
    timeout?: number;
    headers?: Record<string, string>;
  };
}

export function MCPOProvider({ children, client, config }: MCPOProviderProps) {
  const mcpoClient = useMemo(() => {
    return client || new MCPOClient(config);
  }, [client, config]);

  const value = useMemo(() => ({
    client: mcpoClient,
  }), [mcpoClient]);

  return (
    <MCPOContext.Provider value={value}>
      {children}
    </MCPOContext.Provider>
  );
}

/**
 * Hook to access the MCPO client from context
 */
export function useMCPOClient(): MCPOClient {
  const context = useContext(MCPOContext);
  
  if (!context) {
    // Return the default singleton if not in provider
    return mcpoClient;
  }
  
  return context.client;
}