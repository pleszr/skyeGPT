import React, { useState, useEffect } from "react";
import { addMessage, createUserMessage, createBotMessage } from "../utils/MessageManager";

export interface ChatBoxProps {
    title: string;
    askEndpoint: string;
    messages: { sender: "user" | "bot"; text: string }[]; // Expect messages prop
    setMessages: React.Dispatch<React.SetStateAction<{ sender: "user" | "bot"; text: string }[]>>; // Expect setMessages prop
    className: string;
}

const ChatBox: React.FC<ChatBoxProps> = ({ askEndpoint, messages, setMessages, className }) => {
    const [input, setInput] = useState<string>("");
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const sendTechnicalMessage = async (message: string) => {
        setMessages((prev) => [...prev, { sender: "bot", text: message }]);
    };

    useEffect(() => {
            textareaResize();
            hitEnter();
    }, []);

    const scrollToBottom = () => {
        setTimeout(() => {
            const chatContainer = document.querySelector(".skgpt-chatMessages");
    
            if(chatContainer !== null) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
                console.log("scrolling")
            }
        }, 100)
    }

    const hitEnter = () => {
        // Add proper type assertion for button element
        const sendBtn = document.querySelector(".sendBtn") as HTMLElement | null;

        // Add type annotation for input parameter
        document.querySelectorAll(".skgpt-input-textarea").forEach((input: Element) => {
            input.addEventListener("keydown", (e) => {
                if (e instanceof KeyboardEvent) {
                    if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        sendBtn?.click(); // Simplified with optional chaining
                    }
                }
            });
        });
    }

    const sendMessage = async () => {
        if (!input.trim()) return;

        // Add user message
        setMessages((prev) => addMessage(prev, createUserMessage(input)));
        setInput(""); // Clear input field
        scrollToBottom();

        setIsLoading(true);

        const threadId = localStorage.getItem("threadId");
        if (!threadId) {
            await sendTechnicalMessage("No thread ID found. Please wait for the thread to be created.");
            return;
        }
        const chroma_conversation_id = localStorage.getItem("chroma_conversation_id");
        if (!chroma_conversation_id) {
            await sendTechnicalMessage("No chroma_conversation_id found. Please wait for the thread to be created.");
            return;
        }

        try {
            const response = await fetch(askEndpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: input, thread_id: threadId, chroma_conversation_id: chroma_conversation_id }),
            });

            const data = await response.json();
            // Add bot response
            setMessages((prev) => addMessage(prev, createBotMessage(data.answer)));
            scrollToBottom();
        } catch (error) {
            console.log(error);
            // Add error message
            setMessages((prev) => addMessage(prev, createBotMessage("Error: Could not get a response.")));
        } finally {
            setIsLoading(false);
        }
    };

    const textareaResize = () => {
        // Add type assertions to specific HTML elements
        const textarea = document.querySelector(".skgpt-input-textarea") as HTMLTextAreaElement | null;
        const textareaCont = document.querySelector(".skgpt-input") as HTMLElement | null;

        if (textarea && textareaCont) {
            textarea.addEventListener("input", () => {
                textareaCont.style.height = 'auto';
                // Use template literals for better readability
                textareaCont.style.height = `${textarea.scrollHeight + 20}px`;
            }, false);
        }
    }

    return (
        <div className={`skgpt-chatbox ${className}`}>
            <div className="skgpt-chatMessages">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={msg.sender === "user" ? "skgpt-userMesssage" : "skgpt-botMessage"}
                    >
                        {/* Check if the message contains HTML content, if so, use dangerouslySetInnerHTML */}
                        {msg.sender === "bot" ? (
                            <div dangerouslySetInnerHTML={{ __html: msg.text }} />
                        ) : (
                            msg.text // Plain text for the user messages
                        )}
                    </div>
                ))}
                {isLoading && <div className="loading">Loading...</div>}
            </div>
            <div className="skgpt-inputCont">
                <div className="skgpt-input">
                    <textarea
                        rows={1}
                        className="skgpt-input-textarea"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Write your question here..."
                    />
                </div>
                <button className="skgpt-btn primary sendBtn" onClick={sendMessage}>
                    Send
                </button>
            </div>
        </div>
    );
};

export default ChatBox;
