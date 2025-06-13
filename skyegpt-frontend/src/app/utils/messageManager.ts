import { v4 as uuidv4 } from 'uuid';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  stopped: boolean;
  noFeedback?: boolean;
}

const WELCOME_MESSAGE_ID = uuidv4();
const ERROR_MESSAGE_ID = uuidv4();

export const addMessage = (prevMessages: Message[], newMessage: Message): Message[] => {
  return [...prevMessages, newMessage];
};

// added unique ID generation for messages (for frontend only)
export const createBotMessage = (text: string, noFeedback?: boolean): Message => {
  return {
    id: uuidv4(),
    sender: 'bot',
    text,
    timestamp: new Date(),
    stopped: false,
    noFeedback
  };
};

export const createUserMessage = (text: string): Message => {
  return {
    id: uuidv4(),
    sender: 'user',
    text,
    timestamp: new Date(),
    stopped: false
  };
};

export const createWelcomeMessage = (text: string): Message => {
  return {
    id: WELCOME_MESSAGE_ID,
    sender: 'bot',
    text,
    timestamp: new Date(),
    stopped: false,
    noFeedback: true
  };
};

export const createErrorMessage = (text: string): Message => {
  return {
    id: ERROR_MESSAGE_ID,
    sender: 'bot',
    text,
    timestamp: new Date(),
    stopped: false,
    noFeedback: true
  };
};

export const removeWelcomeMessage = (messages: Message[]): Message[] => {
  return messages.filter(msg => msg.id !== WELCOME_MESSAGE_ID);
};