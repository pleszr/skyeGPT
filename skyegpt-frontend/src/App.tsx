import React, { useState, useEffect } from "react";
import ChatBox from "./components/ChatBox";
import "./styles/App.css";
import logo from "./assets/logo.svg";

const App: React.FC = () => {
    const [assistantMessages, setAssistantMessages] = useState<{ sender: "user" | "bot"; text: string }[]>([]);
    const [chromaMessages, setChromaMessages] = useState<{ sender: "user" | "bot"; text: string }[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false); // Add loading state for the entire setup process
    const backendHost = import.meta.env.VITE_SKYEGPT_BACKEND_HOST
        ? `http://${import.meta.env.VITE_SKYEGPT_BACKEND_HOST}`
        : 'http://localhost:8000';
    const createThread = async () => {
        try {
            console.log(isLoading)
            const response = await fetch(`${backendHost}/createThread`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                alert(`Could not create new thread for Assistant, response: ${JSON.stringify(response)}`);
            }

            const data = await response.json();
            console.log("Thread created", data.thread_id);
            localStorage.setItem("threadId", data.thread_id);

            console.log("Chroma conversation created", data.chroma_conversation_id);
            localStorage.setItem("chroma_conversation_id", data.chroma_conversation_id);
        } catch (error) {
            console.error("Error creating thread:", error);
        }
    };

    useEffect(() => {
        createThread(); // Call createThread on mount
        switchTabs(); //call tab switching function
    }, []);

    const sendDefaultSetup = async () => {
        setIsLoading(true); // Start loading
        setAssistantMessages((prevMessages) => [
            ...prevMessages,
            { sender: "bot", text: "Starting default setup..." }, // Display a "starting setup" message
        ]);

        try {
            const response = await fetch("/sample-request.json");
            if (!response.ok) {
                alert(`Could not create default setup for Assistant, response: ${JSON.stringify(response)}`);
            }

            const sampleRequest = await response.json();

            const setupResponse = await fetch(`${backendHost}/setupGptAssistant`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(sampleRequest),
            });

            const data = await setupResponse.json();
            console.log("Setup response:", data);

            // After the setup is complete, display the bot message
            setAssistantMessages((prevMessages) => [
                ...prevMessages,
                { sender: "bot", text: "Default settings have been successfully set!" },
            ]);
        } catch (error) {
            console.error("Error during setup:", error);
            alert("Error: Could not complete default setup.");
        } finally {
            setIsLoading(false); // End loading
        }
    };

    let count = 0;
    const switchTabs = () => {
        const btns = document.querySelectorAll(".tab-header .header-btn");
        const tabs = document.querySelectorAll(".tab-content .gpt-tab")
        if(count < 1) {
            btns.forEach((btn) => {
                btn.addEventListener("click", (e) => {
                    const target = e.currentTarget as HTMLElement | null;
                    if (!target) return; // Ensure `currentTarget` is not null

                    btns.forEach((b) => b.classList.remove("active"));
                    tabs.forEach((b) => b.classList.remove("active"));
                    target.classList.add("active");

                    if (target.classList.contains("assistant")) {
                        document.querySelector(".tab-content .gpt-tab.assistant")?.classList.add("active");
                    } else {
                        document.querySelector(".tab-content .gpt-tab.chroma")?.classList.add("active");
                    }
                });
            });
        }
        count++;
    }

    const askEndpointAssistant = `${backendHost}/askAssistant`;
    const askEndpointChroma = `${backendHost}/askChroma`;
    return (
        <div className="skgpt-app">
            <div className="skgpt-header">
                <button className="skgpt-btn secondary setupButton" onClick={sendDefaultSetup}>
                    Default Setup
                </button>
                <img src={logo} alt="logo" className="skgpt-logo" />
                <span className="credits">design by Fanni Wihl | frontend by Marcell Monoki</span>
            </div>
            <div className="skgpt-appContainer">
                <div className="skgpt-chatContainer">
                    <div className="skgpt-tabs">
                        <div className="tab-header">
                            <div className="header-btn chroma active">Chroma</div>
                            <div className="header-btn assistant">GPT Assistant</div>
                        </div>
                        <div className="tab-content">
                            <div className="gpt-tab chroma active">
                                <ChatBox
                                    title="Ask GPT Chroma"
                                    askEndpoint={askEndpointChroma}
                                    messages={chromaMessages}
                                    setMessages={setChromaMessages}
                                    className="gptChroma"
                                />
                            </div>
                            <div className="gpt-tab assistant">
                                <ChatBox
                                    title="Ask GPT Assistant"
                                    askEndpoint={askEndpointAssistant}
                                    messages={assistantMessages}
                                    setMessages={setAssistantMessages}
                                    className="gptAssistant"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default App;
