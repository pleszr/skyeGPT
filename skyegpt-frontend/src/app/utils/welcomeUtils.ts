export const getTimeBasedGreeting = (): string => {
  const hour = new Date().getHours();
  
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
};

const welcomeMessage = `

I'm SkyeGPT, your AI assistant. 
Please feel free to ask me anything related to Skye, and I'll do my best to assist you.
What can I help you with today?

`;

export const generateWelcomeMessage = (): string => {
  const greeting = getTimeBasedGreeting();
  return `${greeting} 👋! ${welcomeMessage}`;
};