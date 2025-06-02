import { useState, useRef, useCallback } from 'react';
import { addMessage, createUserMessage, createBotMessage, removeWelcomeMessage, Message } from '@/app/utils/messageManager';
import {
  fetchChatResponseStreamAPI,
  getChunkTextFromSSE,
  AskStreamPayload
} from '@/app/services/chatApiService';

export const useStreamingChat = (
  conversationId: string | null,
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>,
  input: string,
  setInput: (value: string) => void
) => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [dynamicLoadingTexts, setDynamicLoadingTexts] = useState<string[]>([]);
  const streamAbortControllerRef = useRef<AbortController | null>(null);

  const sendTechnicalMessage = useCallback(async (messageText: string) => {
    setMessages((prev) => [...prev, createBotMessage(messageText)]);
  }, [setMessages]);

  const processDataChunk = useCallback((
    dataStr: string, 
    allowEmptyChunks: boolean = true,
    fullMessageTextRef: { current: string }
  ) => {
    try {
      if (dataStr === '' || dataStr.trim() === '') {
        if (allowEmptyChunks) {
          fullMessageTextRef.current += dataStr;
          setMessages((prevMsgs) => {
            const newMsgs = [...prevMsgs];
            const lastMsgIndex = newMsgs.length - 1;
            if (lastMsgIndex >= 0 && newMsgs[lastMsgIndex].sender === 'bot') {
              newMsgs[lastMsgIndex] = createBotMessage(fullMessageTextRef.current);
            }
            return newMsgs;
          });
        }
        return;
      }

      let parsedChunk;
      try { 
        parsedChunk = JSON.parse(dataStr); 
      } catch { 
        parsedChunk = { text: dataStr };
      }

      if (parsedChunk && Array.isArray(parsedChunk)) {
        const textsToSet = parsedChunk.map(String).filter(t => t.trim() !== "");
        if (textsToSet.length > 0) setDynamicLoadingTexts(textsToSet);
      } else if (parsedChunk && typeof parsedChunk === 'object' && 'dynamic_loading_text' in parsedChunk) {
        const texts = (parsedChunk as { dynamic_loading_text: string | string[] }).dynamic_loading_text;
        if (Array.isArray(texts)) {
          const textsToSet = texts.map(String).filter(t => t.trim() !== "");
          if (textsToSet.length > 0) setDynamicLoadingTexts(textsToSet);
        } else if (typeof texts === 'string' && texts.trim() !== "") {
          setDynamicLoadingTexts([texts]);
        }
      } else {
        const chunkText = getChunkTextFromSSE(parsedChunk);
        if (chunkText !== null && chunkText !== undefined) { 
          fullMessageTextRef.current += chunkText;
          setMessages((prevMsgs) => {
            const newMsgs = [...prevMsgs];
            const lastMsgIndex = newMsgs.length - 1;
            if (lastMsgIndex >= 0 && newMsgs[lastMsgIndex].sender === 'bot') {
              newMsgs[lastMsgIndex] = createBotMessage(fullMessageTextRef.current);
            }
            return newMsgs;
          });
        }
      }
    } catch (e) { 
      console.warn('Invalid SSE chunk processing error:', e, 'Original dataStr:', dataStr); 
    }
  }, [setMessages]);

  const stopStreaming = useCallback(() => {
    if (streamAbortControllerRef.current) {
      streamAbortControllerRef.current.abort();
    }
    setIsLoading(false);
    setDynamicLoadingTexts([]);
    setMessages(prev => {
      const newMessages = [...prev];
      const lastIndex = newMessages.length - 1;
      if (
        lastIndex >= 0 &&
        newMessages[lastIndex].sender === 'bot' &&
        newMessages[lastIndex].text === ''
      ) {
        newMessages[lastIndex] = { ...createBotMessage("Request cancelled."), stopped: true };
      }
      return newMessages;
    });
  }, [setMessages]);

  const sendMessage = useCallback(async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    setIsLoading(true);
    setDynamicLoadingTexts([]);
    if (streamAbortControllerRef.current) streamAbortControllerRef.current.abort();
    streamAbortControllerRef.current = new AbortController();

    setMessages((prev) => {
      const messagesWithoutWelcome = removeWelcomeMessage(prev);
      return addMessage(messagesWithoutWelcome, createUserMessage(trimmedInput));
    });
    setInput('');

    if (!conversationId) {
      await sendTechnicalMessage('Error: Conversation ID not available. Please refresh or try again.');
      setIsLoading(false);
      return;
    }

    const hiddenInstruction = "Output:GitHubFlavoredMarkdown. No ```markdown``` fences. standard GFM for all elements, no screenshots, use `##` for headings Use `\\n` for line breaks.";
    const queryToSendToBackend = `User query: ${trimmedInput}\nFormat Instruction: ${hiddenInstruction}`;
    const fullMessageTextRef = { current: '' };

    const fetchStreamSingleAttempt = async (): Promise<boolean> => {
      fullMessageTextRef.current = '';
      setMessages((prev) => addMessage(prev, createBotMessage('')));
      try {
        const payload: AskStreamPayload = { conversation_id: conversationId, query: queryToSendToBackend };
        const response = await fetchChatResponseStreamAPI(payload, streamAbortControllerRef.current!.signal);
        const reader = response.body?.getReader();
        if (!reader) throw new Error('Failed to get stream reader from response.');
        let buffer = '';
        
        while (true) {
          if (streamAbortControllerRef.current?.signal.aborted) {
            reader.cancel();
            throw new Error("Stream aborted");
          }
          
          const { value, done } = await reader.read();
          if (done) {
            if (!fullMessageTextRef.current.trim()) {
              setMessages((prev) => {
                const newMessages = [...prev];
                const lastMessageIndex = newMessages.length - 1;
                if (lastMessageIndex >= 0 && newMessages[lastMessageIndex].sender === 'bot') {
                  newMessages[lastMessageIndex] = createBotMessage("No response received from the server. Please try again.");
                }
                return newMessages;
              });
            } else {
              setMessages((prevMsgs) => {
                const newMsgs = [...prevMsgs];
                const lastMsgIndex = newMsgs.length - 1;
                if (lastMsgIndex >= 0 && newMsgs[lastMsgIndex].sender === 'bot' && newMsgs[lastMsgIndex].text !== fullMessageTextRef.current) {
                  newMsgs[lastMsgIndex] = createBotMessage(fullMessageTextRef.current);
                }
                return newMsgs;
              });
            }
            setDynamicLoadingTexts([]);
            return !(!fullMessageTextRef.current.trim());
          }
          
          buffer += new TextDecoder().decode(value);

          const newlineChunks = buffer.split('\n');
          const lastChunk = newlineChunks.pop() || '';

          const completeLines = newlineChunks.filter(line => {
            const trimmed = line.trim();
            return line !== '' && trimmed !== '\r';
          });

          if (completeLines.length > 0) {
            buffer = lastChunk;
            for (const line of completeLines) {
              if (streamAbortControllerRef.current?.signal.aborted) break;
              
              if (line.startsWith('data: ')) {
                const dataStr = line.slice(6);
                processDataChunk(dataStr, true, fullMessageTextRef);
              }
            }
          } else {
            const spaceChunks = buffer.split(' ');
            if (spaceChunks.length > 1) {
              buffer = spaceChunks.pop() || '';
              for (const chunk of spaceChunks) {
                if (streamAbortControllerRef.current?.signal.aborted) break;
                if (chunk.startsWith('data: ')) {
                  const dataStr = chunk.slice(6);
                  processDataChunk(dataStr, false, fullMessageTextRef);
                }
              }
            } else {
              buffer = lastChunk;
            }
          }
        }
      } catch (error: unknown) {
        if (typeof error === 'object' && error !== null && (('name' in error && (error as { name: string }).name === 'AbortError') || ('message' in error && (error as { message: string }).message === "Stream aborted"))) {
          setMessages(prev => {
            const newMessages = [...prev]; 
            const lastMessageIndex = newMessages.length - 1;
            if (lastMessageIndex >= 0 && newMessages[lastMessageIndex].sender === 'bot') {
              newMessages[lastMessageIndex] = { ...newMessages[lastMessageIndex], text: "Request cancelled.", stopped: true };
            } 
            return newMessages;
          });
        } else {
          const errorMessage = error instanceof Error ? error.message : "An unexpected error occurred. Please try again.";
          setMessages((prev) => {
            const newMessages = [...prev]; 
            const lastMessageIndex = newMessages.length - 1;
            if (lastMessageIndex >= 0 && newMessages[lastMessageIndex]?.sender === 'bot') {
              newMessages[lastMessageIndex] = createBotMessage(`Error: ${errorMessage}`);
            } else {
              addMessage(newMessages, createBotMessage(`Error: ${errorMessage}`));
            }
            return newMessages;
          });
        }
        setDynamicLoadingTexts([]); 
        return false;
      }
    };
    
    await fetchStreamSingleAttempt();
    setIsLoading(false);
  }, [input, isLoading, setMessages, sendTechnicalMessage, conversationId, processDataChunk, setInput]);

  return {
    isLoading,
    dynamicLoadingTexts,
    sendMessage,
    stopStreaming
  };
};