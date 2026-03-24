import apiClient from './apiClient';
import type {
  SpellcheckRequest,
  SpellcheckResponse,
  TranslateRequest,
  TranslateResponse,
  LemmatizeRequest,
  LemmatizeResponse,
  TTSRequest,
  TTSResponse,
  ChatRequest,
  ChatResponse,
  AutocompleteRequest,
  AutocompleteResponse,
  NLPInsightsRequest,
  NLPInsightsResponse,
} from '@/types';

export const spellcheckService = {
  check: async (data: SpellcheckRequest): Promise<SpellcheckResponse> => {
    const res = await apiClient.post<SpellcheckResponse>('/spellcheck', data);
    return res.data;
  },
};

export const translateService = {
  translate: async (data: TranslateRequest): Promise<TranslateResponse> => {
    const res = await apiClient.post<TranslateResponse>('/translate', data);
    return res.data;
  },
};

export const lemmatizeService = {
  lemmatize: async (data: LemmatizeRequest): Promise<LemmatizeResponse> => {
    const res = await apiClient.post<LemmatizeResponse>('/lemmatize', data);
    return res.data;
  },
};

export const ttsService = {
  synthesize: async (data: TTSRequest): Promise<TTSResponse> => {
    const res = await apiClient.post<TTSResponse>('/tts', data);
    return res.data;
  },
};

export const chatService = {
  send: async (data: ChatRequest): Promise<ChatResponse> => {
    const res = await apiClient.post<ChatResponse>('/chat', data);
    return res.data;
  },
};

export const autocompleteService = {
  suggest: async (data: AutocompleteRequest): Promise<AutocompleteResponse> => {
    const res = await apiClient.post<AutocompleteResponse>('/autocomplete', data);
    return res.data;
  },
};

export const nlpService = {
  analyze: async (data: NLPInsightsRequest): Promise<NLPInsightsResponse> => {
    const res = await apiClient.post<NLPInsightsResponse>('/nlp/insights', data);
    return res.data;
  },
};
