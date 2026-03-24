import apiClient from './apiClient';
import type {
  TranslateRequest,
  TranslateResponse,
  TTSRequest,
  TTSResponse,
  ChatRequest,
  ChatResponse,
  AutocompleteRequest,
  AutocompleteResponse,
  NLPInsightsRequest,
  NLPInsightsResponse,
} from '@/types';

export const translateService = {
  translate: async (data: TranslateRequest): Promise<TranslateResponse> => {
    // Adapter les noms de champs : sourceLang/targetLang → from/to
    const res = await apiClient.post<{ translation: string }>('/translate', {
      text: data.text,
      from: data.sourceLang,
      to: data.targetLang,
    });
    return { translatedText: res.data.translation };
  },
};

export const ttsService = {
  synthesize: async (data: TTSRequest): Promise<TTSResponse> => {
    const res = await apiClient.post<{ audio: string; format: string; mimeType: string }>('/tts', data);
    // Construire l'URL data: à partir du base64
    return { audioUrl: `data:${res.data.mimeType};base64,${res.data.audio}` };
  },
};

export const chatService = {
  send: async (data: ChatRequest): Promise<ChatResponse> => {
    // Adapter le format de l'historique : content → text, assistant → model
    const res = await apiClient.post<ChatResponse>('/chat', {
      message: data.message,
      history: data.history.map((h) => ({
        role: h.role === 'assistant' ? 'model' : h.role,
        text: h.content,
      })),
    });
    return res.data;
  },
};

export const autocompleteService = {
  suggest: async (data: AutocompleteRequest): Promise<AutocompleteResponse> => {
    // Le proxy utilise GET avec query param
    const res = await apiClient.get<{ suggestions: string[]; type?: 'prediction' | 'correction'; error?: string }>(
      '/autocomplete',
      { params: { text: data.text } }
    );
    return {
      suggestions: (res.data.suggestions || []).map((s, i) => ({
        text: s,
        score: 1 - i * 0.1,
      })),
      type: res.data.type,
    };
  },
};

export const nlpService = {
  analyze: async (data: NLPInsightsRequest): Promise<NLPInsightsResponse> => {
    // NER et Sentiment via deux appels parallèles
    const [nerRes, sentRes] = await Promise.all([
      apiClient.post<{ entities: Array<{ name: string; type: string; salience: number }> }>('/ner', { text: data.text }),
      apiClient.post<{ score: number; magnitude: number; label: string }>('/sentiment', { text: data.text }),
    ]);

    const words = data.text.split(/\s+/).filter(Boolean);
    return {
      entities: nerRes.data.entities.map((e) => ({
        text: e.name,
        label: e.type,
        start: 0,
        end: 0,
      })),
      sentiment: {
        label: sentRes.data.label,
        score: sentRes.data.score,
      },
      wordCount: words.length,
      charCount: data.text.length,
    };
  },
};
