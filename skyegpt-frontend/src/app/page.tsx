'use client';

import Image from 'next/image';
import React, { useState, useEffect } from 'react';
import ChatBox from '@/app/components/chatBox';
import { backendHost } from '@/app/utils/sharedConfig';
import { Message } from '@/app/utils/messageManager';

const HomePage = () => {
  const [chromaMessages, setChromaMessages] = useState<Message[]>([]);

  const createConversation = async () => {
    try {
      const response = await fetch(`${backendHost}/ask/conversation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Could not create new conversation: ${response.status}`);
      }

      const data = await response.json();
      console.log('Conversation created', data.conversation_id);
      localStorage.setItem('chroma_conversation_id', data.conversation_id);

    } catch (error) {
      console.error('Error creating conversation:', error);
      alert('Failed to create conversation. Please try again.');
    }
  };

  useEffect(() => {
    createConversation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const askEndpointChroma = `${backendHost}/ask/response/stream`;

  return (
    <div className="w-screen min-h-screen max-w-full flex flex-col overflow-hidden bg-gray-50"> 
      <div className="flex-1 md:items-center flex flex-col md:flex-row mx-auto w-full max-w-[1530px] px-4 sm:px-8 md:px-12 overflow-hidden">
        
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
            alt="SkyeGPT logo"
            width={191}
            height={149}
            className="w-auto h-auto max-w-[150px] max-h-[100px] sm:max-h-[120px]"
          />
        </div>

        <div className="flex-1 flex flex-col min-h-0 pb-4 md:pb-0"> 
          <div className="flex flex-col min-h-0 pt-0 sm:pt-2 md:pt-15 pb-4 sm:pb-6 w-full h-full"> 
            <div className="flex flex-col ">
              
              <div className="flex-1 bg-white shadow-lg rounded-[30px] sm:rounded-[40px] p-0 min-h-0 overflow-hidden"> 
                <div className="h-full"> 
                  <ChatBox
                    askEndpoint={askEndpointChroma}
                    messages={chromaMessages}
                    setMessages={setChromaMessages}
                    className="gptChroma" 
                  />
                </div>
              </div>
            </div>
          </div>
          
          <footer className="text-center text-xs sm:text-sm text-gray-600 py-3 sm:py-4 shrink-0">
            SkyeGPT can make mistakes. If you find the answer strange, verify the results and give feedback!
          </footer>
        </div>
      </div>
    </div>
  );
};

export default HomePage;