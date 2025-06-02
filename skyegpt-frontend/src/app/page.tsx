'use client';

import Image from 'next/image';
import React, { useState, useEffect } from 'react';
import ChatBox from '@/app/components/chatBox';
import { Message, createWelcomeMessage } from '@/app/utils/messageManager';
import { createConversationAPI, ConversationResponse } from '@/app/services/chatApiService';
import { generateWelcomeMessage } from '@/app/utils/welcomeUtils';

const HomePage = () => {
  const [messages, setMessages] = useState<Message[]>([
    createWelcomeMessage(generateWelcomeMessage())
  ]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<string>('10.0');

  const initializeConversation = async () => {
    try {
      const data: ConversationResponse = await createConversationAPI();
      setCurrentConversationId(data.conversation_id);
      console.log("New conversation created", data.conversation_id);
    } catch (error) {
      console.error('Failed to initialize conversation:', error);
      alert(`Failed to start a new chat session. Please try refreshing the page. Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  useEffect(() => {
    initializeConversation();
  }, []);

  // PLACEHOLDER
  const versions = ['10.0'];

  return (
    <div className="w-screen min-h-screen max-w-full flex flex-col overflow-hidden bg-gray-50">
      <div className="flex-1 md:items-center flex flex-col md:flex-row mx-auto w-full max-w-[1530px] px-4 sm:px-8 md:px-12 overflow-hidden relative">
        <div className="skgpt-version-selector absolute sm:top-[170px] md:top-6 right-6 flex items-center gap-2">
          <span className="text-base font-normal text-black">VERSION:</span>
          <div className="relative inline-block text-left">
            <select
              aria-label="Select version"
              value={selectedVersion}
              onChange={(e) => setSelectedVersion(e.target.value)}
              className="appearance-none bg-transparent border-none text-base font-bold text-black pr-4 cursor-pointer"
            >
              {versions.map((version) => (
                <option key={version} value={version}>
                  {version}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center">
              <svg
                width="13"
                height="9"
                viewBox="0 0 13 9"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M5.54239 8.37933L0.44398 3.28093C0.09159 2.92854 0.09159 2.35871 0.44398 2.01007L1.29122 1.16284C1.6436 0.810447 2.21343 0.810447 2.56207 1.16284L6.17969 4.77296L9.79356 1.15909C10.1459 0.806698 10.7158 0.806698 11.0644 1.15909L11.9154 2.00632C12.2678 2.35871 12.2678 2.92854 11.9154 3.27718L6.81699 8.37558C6.4646 8.73172 5.89478 8.73172 5.54239 8.37933Z"
                  fill="#24272A"
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="hidden md:flex flex-col items-center justify-start w-[200px] md:w-[300px] py-4 md:py-8 px-2 relative shrink-0 space-y-4 md:space-y-6">
          <div className="w-full flex justify-center flex-shrink-0 px-4">
            <Image
              src="/logo.png"
              alt="SkyeGPT logo"
              width={191}
              height={149}
              className="object-contain w-auto h-full max-w-[60%] sm:max-w-[50%] md:max-w-[291px] max-h-[15vh]"
            />
          </div>
          <div className="w-full flex justify-center flex-shrink-0 px-4">
            <Image
              src="/gears.png"
              alt="Gears"
              width={267}
              height={380}
              className="object-contain w-auto h-full max-w-[50%] sm:max-w-[40%] md:max-w-[200px] max-h-[30vh]"
            />
          </div>
          <div className="w-full flex justify-center flex-shrink-0 min-h-0 items-end px-4">
            <Image
              src="/robot.png"
              alt="Robot"
              width={300}
              height={300}
              priority
              className="object-contain w-auto h-full max-w-[90%] md:max-w-full max-h-[35vh] md:max-h-[40vh] relative -mr-4 md:-mr-19"
            />
          </div>
        </div>

        <div className="flex md:hidden justify-center py-6 sm:py-8 shrink-0">
          <Image
            src="/logo.png"
            alt="SkyeGPT mobile logo"
            width={191}
            height={149}
            className="w-auto h-auto max-w-[150px] max-h-[100px] sm:max-h-[120px]"
          />
        </div>

        <div className="flex-1 flex flex-col min-h-0 pb-4 md:pb-0">
          <div className="flex flex-col min-h-0 pt-0 sm:pt-2 md:pt-15 pb-4 sm:pb-6 w-full h-full">
            <div className="flex flex-col">
              <div className="flex-1 bg-white shadow-lg rounded-[30px] sm:rounded-[40px] p-0 min-h-0 overflow-hidden">
                <div className="h-full">
                  <ChatBox
                    messages={messages}
                    setMessages={setMessages}
                    className="gpt"
                    conversationId={currentConversationId}
                  />
                </div>
              </div>
            </div>
            <footer className="text-center text-xs sm:text-sm text-gray-600 py-3 sm:py-4 shrink-0">
            SkyeGPT can make mistakes. If you find the answer strange, verify the results and give feedback!
          </footer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;