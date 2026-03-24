// ─── Spellcheck ───
export interface SpellcheckRequest {
  text: string;
}

export interface SpellError {
  word: string;
  offset: number;
  length: number;
  suggestions: string[];
}

export interface SpellcheckResponse {
  errors: SpellError[];
}

// ─── Translation ───
export interface TranslateRequest {
  text: string;
  sourceLang: string;
  targetLang: string;
}

export interface TranslateResponse {
  translatedText: string;
}

// ─── Lemmatization ───
export interface LemmatizeRequest {
  word: string;
}

export interface LemmatizeResponse {
  lemma: string;
  pos: string;
  morphology: string[];
}

// ─── Text-to-Speech ───
export interface TTSRequest {
  text: string;
}

export interface TTSResponse {
  audioUrl: string;
}

// ─── Chatbot ───
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface ChatRequest {
  message: string;
  history: Pick<ChatMessage, 'role' | 'content'>[];
}

export interface ChatResponse {
  reply: string;
}

// ─── Autocomplete ───
export interface AutocompleteRequest {
  text: string;
  cursorPosition: number;
}

export interface AutocompleteSuggestion {
  text: string;
  score: number;
}

export interface AutocompleteResponse {
  suggestions: AutocompleteSuggestion[];
}

// ─── NLP Insights ───
export interface NEREntity {
  text: string;
  label: string;
  start: number;
  end: number;
}

export interface NLPInsightsRequest {
  text: string;
}

export interface NLPInsightsResponse {
  entities: NEREntity[];
  sentiment: {
    label: string;
    score: number;
  };
  wordCount: number;
  charCount: number;
}

// ─── Generic API ───
export interface ApiError {
  message: string;
  status: number;
  details?: unknown;
}
