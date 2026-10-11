/** One scripted answer in the chat tree. */
export type ChatNode = {
  id: string;
  /** Text shown on the suggestion chip. Absent on the fallback node. */
  label?: string;
  /** Lowercase substrings matched against free-typed input. */
  keywords?: string[];
  answer: string;
  /** Node ids offered as follow-up chips after this answer. */
  followUps: string[];
  /** Whether to show the "go to contact form" action with this answer. */
  offerContact: boolean;
};

export type ChatScript = {
  initialSuggestions: string[];
  fallback: ChatNode;
  nodes: Record<string, ChatNode>;
};
