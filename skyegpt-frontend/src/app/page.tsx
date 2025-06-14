'use client';

import Image from 'next/image';
import React, { useState, useEffect } from 'react';
import ChatBox from '@/app/components/chatBox';
import { Message, createErrorMessage, createWelcomeMessage } from '@/app/utils/messageManager';
import { createConversationAPI, ConversationResponse } from '@/app/services/chatApiService';
import { getVersion } from '@/app/utils/sharedConfig';
import { generateWelcomeMessage } from '@/app/utils/welcomeUtils';

const HomePage = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<string>('10.0');
  const [appVersion, setAppVersion] = useState<string>('');

  const initializeConversation = async () => {
    try {
      const data: ConversationResponse = await createConversationAPI();
      setCurrentConversationId(data.conversation_id);
      console.log("New conversation created", data.conversation_id);

      setMessages([createWelcomeMessage(generateWelcomeMessage())]);
    } catch (error) {
      console.error('Failed to initialize conversation:', error);
      setMessages([createErrorMessage('Failed to initialize conversation. Please try again later. Error message: ' +  (error instanceof Error ? error.message : 'Unknown error'))]);
    }
  };

  const loadVersion = async () => {
    try {
      const version = await getVersion();
      if (version && version !== '9.9.9.9') {
        setAppVersion(version);
      }
      console.log("App version loaded:", version);
    } catch (error) {
      console.error('Failed to load app version:', error);
    }
  };

  useEffect(() => {
    initializeConversation();
    loadVersion();
  }, []);

  // PLACEHOLDER
  const versions = ['10.0'];

  return (
      <div className="w-screen min-h-screen max-w-full flex flex-col overflow-hidden bg-gray-50">
        <div className="flex-1 lg:items-center flex flex-col lg:flex-row mx-auto w-full max-w-[1530px] px-4 sm:px-8 lg:px-12 overflow-hidden relative min-w-0">
          <div className="skgpt-version-selector absolute sm:top-[170px] lg:top-6 right-6 flex items-center gap-2 z-10">
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
                <Image
                    src="/versionselector.png"
                    alt="Version selector dropdown icon"
                    width={32}
                    height={32}
                    priority
                    quality={100}
                    className="object-contain max-w-[32px] max-h-[32px] w-auto h-auto"
                />
              </div>
            </div>
          </div>

          <div className="hidden lg:flex flex-col items-center justify-start w-[200px] lg:w-[300px] py-4 lg:py-8 px-2 relative shrink-0 space-y-4 lg:space-y-6 min-w-0">
            <div className="w-full flex justify-center flex-shrink-0 px-4">
              <Image
                  src="/logo.png"
                  alt="SkyeGPT logo"
                  width={191}
                  height={149}
                  priority
                  quality={100}
                  className="object-contain w-auto h-full max-w-[60%] sm:max-w-[50%] lg:max-w-[291px] max-h-[15vh]"
              />
            </div>
            <div className="w-full flex justify-center flex-shrink-0 px-4">
              <Image
                  src="/gears.png"
                  alt="Gears"
                  width={267}
                  height={380}
                  priority
                  quality={100}
                  className="object-contain w-auto h-full max-w-[50%] sm:max-w-[40%] lg:max-w-[200px] max-h-[30vh]"
              />
            </div>
            <div className="w-full flex justify-center flex-shrink-0 min-h-0 items-end px-4">
              <Image
                  src="/robot.png"
                  alt="Robot"
                  width={300}
                  height={300}
                  priority
                  quality={100}
                  className="object-contain w-auto h-full max-w-[110%] lg:max-w-[120%] max-h-[45vh] lg:max-h-[50vh] relative -mr-4 lg:-mr-15"
              />
            </div>
          </div>

          <div className="flex lg:hidden justify-center py-6 sm:py-8 shrink-0">
            <Image
                src="/logo.png"
                alt="SkyeGPT mobile logo"
                width={191}
                height={149}
                priority
                quality={100}
                className="w-auto h-auto max-w-[150px] max-h-[100px] sm:max-h-[120px]"
            />
          </div>

          <div className="flex-1 flex flex-col min-h-0 pb-4 lg:pb-0 min-w-0 overflow-hidden">
            <div className="flex flex-col min-h-0 pt-0 sm:pt-2 lg:pt-15 pb-4 sm:pb-6 w-full h-full min-w-0">
              <div className="flex flex-col min-w-0">
                <div className="flex-1 bg-white shadow-lg rounded-[30px] sm:rounded-[40px] p-0 min-h-0 overflow-hidden min-w-0">
                  <div className="h-full min-w-0 overflow-hidden">
                    <ChatBox
                        messages={messages}
                        setMessages={setMessages}
                        className="gpt"
                        conversationId={currentConversationId}
                    />
                  </div>
                </div>
              </div>
            </div>
            <footer className="text-center text-xs sm:text-sm text-gray-600 shrink-0">
              {appVersion && appVersion !== '' && appVersion !== '9.9.9.9' && (
                  <div className="text-center text-xs text-gray-500 shrink-0">
                    v{appVersion}
                  </div>
              )}
              SkyeGPT can make mistakes. If you find the answer strange, verify the results and give feedback!
            </footer>
          </div>
        </div>
      </div>
  );
};

export default HomePage;