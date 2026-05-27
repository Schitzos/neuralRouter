import { useState, useEffect } from 'react';

interface Provider {
  name: string;
  envKey: string;
  hasKey: boolean;
}

const PROVIDERS_STORAGE_KEY = 'schitzo_providers';

interface ModelProvidersProps {
  apiUrl: string;
}

export const ModelProviders: React.FC<ModelProvidersProps> = ({ apiUrl }) => {
  const [providers, setProviders] = useState<Provider[]>([
    { name: 'Gemini', envKey: 'GEMINI_API_KEY', hasKey: false },
    { name: 'Moonshot / Kimi', envKey: 'MOONSHOT_API_KEY', hasKey: false },
    { name: 'OpenAI', envKey: 'OPENAI_API_KEY', hasKey: false },
    { name: 'Anthropic', envKey: 'ANTHROPIC_API_KEY', hasKey: false },
  ]);
  const [editingProvider, setEditingProvider] = useState<string | null>(null);
  const [keyInput, setKeyInput] = useState('');
  const [savedKeys, setSavedKeys] = useState<Record<string, string>>({});

  useEffect(() => {
    try {
      const stored = localStorage.getItem(PROVIDERS_STORAGE_KEY);
      if (stored) {
        const keys = JSON.parse(stored) as Record<string, string>;
        setSavedKeys(keys);
        setProviders(prev => prev.map(p => ({
          ...p,
          hasKey: !!keys[p.envKey]
        })));
      }
    } catch {}
  }, []);

  const saveKey = (envKey: string) => {
    const updated = { ...savedKeys, [envKey]: keyInput };
    setSavedKeys(updated);
    localStorage.setItem(PROVIDERS_STORAGE_KEY, JSON.stringify(updated));
    setProviders(prev => prev.map(p =>
      p.envKey === envKey ? { ...p, hasKey: true } : p
    ));
    setEditingProvider(null);
    setKeyInput('');
  };

  const removeKey = (envKey: string) => {
    const updated = { ...savedKeys };
    delete updated[envKey];
    setSavedKeys(updated);
    localStorage.setItem(PROVIDERS_STORAGE_KEY, JSON.stringify(updated));
    setProviders(prev => prev.map(p =>
      p.envKey === envKey ? { ...p, hasKey: false } : p
    ));
  };

  return (
    <div style={{ display: 'grid', gap: '8px' }}>
      {providers.map(provider => (
        <div key={provider.envKey} style={{
          display: 'flex', alignItems: 'center', gap: '12px',
          padding: '12px', background: '#f9fafb', borderRadius: '8px', border: '1px solid #e5e7eb'
        }}>
          <span style={{ fontWeight: 600, minWidth: '140px' }}>{provider.name}</span>
          <span style={{ fontSize: '12px', color: '#6b7280', minWidth: '160px' }}>{provider.envKey}</span>

          {editingProvider === provider.envKey ? (
            <div style={{ display: 'flex', gap: '8px', flex: 1 }}>
              <input
                type="password"
                value={keyInput}
                onChange={e => setKeyInput(e.target.value)}
                placeholder="Enter API key..."
                style={{ flex: 1, padding: '6px 10px', borderRadius: '4px', border: '1px solid #d1d5db', fontSize: '13px' }}
              />
              <button onClick={() => saveKey(provider.envKey)} style={{ padding: '6px 12px', background: '#10b981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                Save
              </button>
              <button onClick={() => { setEditingProvider(null); setKeyInput(''); }} style={{ padding: '6px 12px', background: '#6b7280', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                Cancel
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', color: provider.hasKey ? '#10b981' : '#ef4444' }}>
                {provider.hasKey ? '● Configured' : '○ Not set'}
              </span>
              <button onClick={() => setEditingProvider(provider.envKey)} style={{ padding: '4px 10px', fontSize: '12px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                {provider.hasKey ? 'Update' : 'Add Key'}
              </button>
              {provider.hasKey && (
                <button onClick={() => removeKey(provider.envKey)} style={{ padding: '4px 10px', fontSize: '12px', background: '#ef4444', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  Remove
                </button>
              )}
            </div>
          )}
        </div>
      ))}
      <p style={{ fontSize: '11px', color: '#9ca3af', marginTop: '8px' }}>
        Note: Keys saved here are stored in your browser. For production, set them in the .env file and restart the router.
      </p>
    </div>
  );
};
