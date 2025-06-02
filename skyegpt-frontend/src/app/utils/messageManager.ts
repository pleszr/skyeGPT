export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  stopped: boolean;
  noFeedback?: boolean;
}

export const addMessage = (prevMessages: Message[], newMessage: Message): Message[] => {
  return [...prevMessages, newMessage];
};

// added unique ID generation for messages (for frontend only)
export const createBotMessage = (text: string, noFeedback?: boolean): Message => {
  return { 
    id: crypto.randomUUID(), 
    sender: 'bot', 
    text, 
    timestamp: new Date(), 
    stopped: false,
    noFeedback 
  };
};

export const createUserMessage = (text: string): Message => {
  return { 
    id: crypto.randomUUID(), 
    sender: 'user', 
    text, 
    timestamp: new Date(), 
    stopped: false 
  };
};

export const createWelcomeMessage = (text: string): Message => {
  return {
    id: 'welcome-message',
    sender: 'bot',
    text,
    timestamp: new Date(),
    stopped: false,
    noFeedback: true
  };
};

export const removeWelcomeMessage = (messages: Message[]): Message[] => {
  return messages.filter(msg => msg.id !== 'welcome-message');
};