import { useState, useEffect, useCallback, useRef } from 'react';

export function useFetch(fetcher, deps = [], options = {}) {
  const { immediate = true, initialData = null } = options;
  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);
  const mountedRef = useRef(true);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetcher();
      if (mountedRef.current) setData(res.data);
    } catch (e) {
      if (mountedRef.current) {
        setError(e.response?.data?.detail || e.message || 'Something went wrong');
      }
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, deps);

  useEffect(() => {
    mountedRef.current = true;
    if (immediate) reload();
    return () => { mountedRef.current = false; };
  }, [reload, immediate]);

  return { data, loading, error, reload, setData };
}

export function useMutation(mutationFn, options = {}) {
  const { onSuccess, onError } = options;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const mutate = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);
      try {
        const res = await mutationFn(...args);
        onSuccess?.(res.data, ...args);
        return res.data;
      } catch (e) {
        const msg = e.response?.data?.detail || e.message;
        setError(msg);
        onError?.(msg);
        throw e;
      } finally {
        setLoading(false);
      }
    },
    [mutationFn, onSuccess, onError]
  );

  return { mutate, loading, error };
}

export function useDebounce(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}