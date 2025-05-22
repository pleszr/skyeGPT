# SkyeGPT - Frontend Setup Guide

This README explains how to set up and run the SkyeGPT frontend. 

## Table of Contents

- [Build Options](#build-options)
- [Set Up Your Environment – Local](#set-up-your-environment--local)
  - [Install deps (node, npm)](#install-deps-node-npm)
    - [Windows 11 (with winget)](#windows-11-with-winget)
    - [Linux](#linux)
    - [macOS](#macos)
- [Set Up Your Environment – Docker](#set-up-your-environment--docker)
  - [With Docker-Compose](#with-docker-compose)
  - [With Docker](#with-docker)
- [Start Development](#start-development)
- [Project Structure](#project-structure)
  - [chatBox.tsx](#chatboxtsx)
  - [chatApiService.ts](#chatapiservicets)
  - ~~[submitFeedback/route.tsx](#submitfeedbackroutetsx)~~
  - ~~[submitRating/route.tsx](#submitratingroutetsx)~~
  - [messageManager.ts](#messagemanagerts)
  - [sharedConfig.ts](#sharedconfigts)
  - [layout.tsx](#layouttsx)
  - [page.tsx](#pagetsx)
- [Notes](#notes)


## Build Options

1. **Local** (for development, with HMR)
2. **Docker** (For PROD readiness, for perform PROD-like testing. no hot-reload, HMR)

## Set Up Your Environment  [**Local**]

You need to install npm and the required packages, then start the development server. 

The frontend uses 
- **NextJS** and 
- **Tailwind CSS**. 
- Use **Node.js version 22 LTS**.
- Port **5173**

### Install deps (node, npm)

#### Windows 11 (with winget)

```bash
# Install fnm (Node version manager)
winget install Schniz.fnm

# Install Node.js version 22
fnm install 22

# Check Node.js version (should show v22.15.0)
node -v

# Check npm version (should show 10.9.2)
npm -v
```

#### Linux

```bash
# Install fnm
curl -o- https://fnm.vercel.app/install | bash

# Install Node.js version 22
fnm install 22

# Check Node.js version (should show v22.15.0)
node -v

# Check npm version (should show 10.9.2)
npm -v
```

#### macOS

```bash
# Install Homebrew
curl -o- https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh | bash

# Install Node.js version 22
brew install node@22

# Check Node.js version (should show v22.15.0)
node -v

# Check npm version (should show 10.9.2)
npm -v
```

## Set Up Your Environment  [**Docker**]
! Suitable For PROD readiness, for perform PROD-like testing. (no hot-reload, HMR)

#### With Docker-Compose

```bash
# cd to root
cd skyeGPT

# Build frontend
docker compose build frontend --no-cache

# Run frontend
docker compose up frontend

# Check the built frontend
localhost:5173
```

#### With Docker

```bash
# cd skyegpt-frontend
cd skyegpt-frontend

# Build frontend
docker build -t skyegpt-frontend .

# Run frontend
docker run --rm -it -p 5173:5173 skyegpt-frontend

# Check the built frontend
localhost:5173
```


## Start Development

Run these commands to start the development server:

```bash
cd skyegpt-frontend
npm install
npm run dev
```





## Project Structure

Here’s the folder and file structure of the `skyegpt-frontend` project:

- **Folders**:
  - `__tests__/` (Test files)
  - `public/` (Static assets)
  - `src/` (Source code)

- **Inside `src/`**:
  - `app/` (Main app folder)
    - `components/` (React components)
      - `chatBox.tsx` (Chat interface component)
    - `mock/` (Mock API data)
      - `api/`
        - `submitFeedback/` (Feedback API mock)
        - `submitRating/` (Rating API mock)
    - `utils/` (Utility functions)
      - `messageManager.ts` (Handles messages)
      - `sharedConfig.ts` (Backend host config)
    - `services/` (Services)
      - `chatApiService.ts` (Backend APIs)
    - `favicon.ico` (Site icon)
    - `globals.css` (Global styles)
    - `layout.tsx` (Root layout)
    - `page.tsx` (Main page, HomePage)

---

### `chatBox.tsx`

This is the main chat interface component. It handles user input, displays messages, and supports feedback (thumbs up/down and text feedback).

- **Features**:
  - Sends user messages to the backend.
  - Streams bot responses using Server-Sent Events (SSE).
  - Supports Markdown rendering with GitHub Flavored Markdown (GFM).
  - Allows users to give thumbs-up/down ratings and detailed feedback.
  - Shows loading animations and error messages.

- **Key Functions**:
  - `sendMessage`: Sends user input to the backend and streams the response.
  - `handleFeedbackSubmit`: Submits user feedback (text and rating).
  - `debouncedHandleRating`: Handles thumbs-up/down ratings with a delay to avoid rapid clicks.
  - `scrollToBottom`: Smoothly scrolls to the latest message.

---

### `chatApiService.ts`


This module provides API interaction utilities for the chat functionality. (Backend URLS)

- It centralizes backend endpoints
- defines data interfaces
- functions for creating conversations, streaming messages, and submitting feedback. 



- **Backend URLs**
  - `API_BASE_URL`: Root URL for the backend.
  - `CREATE_CONVERSATION_URL`: `POST /ask/conversation`
  - `ASK_STREAM_URL`: `POST /ask/response/stream`
  - `getConversationFeedbackUrl(conversationId)`: Constructs feedback endpoint URL for a given conversation.

---

// FOR TESTING - NOT USED
### ~~`submitFeedback/route.tsx`~~

~~This is a mock API route for submitting feedback.~~

- ~~**Function**:~~  
  ~~Accepts POST requests with feedback data (message index, feedback text, rating, conversation ID).~~  
  ~~Validates input and stores feedback in an in-memory array.~~  
  ~~Returns success or error responses.~~

- ~~**GET Request**:~~  
  ~~Returns all stored feedback entries.~~  

---

### ~~`submitRating/route.tsx`~~

~~This is a mock API route for submitting thumbs-up/down ratings.~~

- ~~**Function**:~~  
  ~~Accepts POST requests with rating data (message index, rating, conversation ID).~~  
  ~~Validates input and stores ratings in an in-memory array.~~  
  ~~Returns success or error responses.~~

- ~~**GET Request**:~~  
  ~~Returns all stored ratings.~~

---

### `messageManager.ts`

Utility functions for managing chat messages.

- **Functions**:
  - `addMessage`: Adds a new message to the message list.
  - `createUserMessage`: Creates a user message object.
  - `createBotMessage`: Creates a bot message object.

---

### `sharedConfig.ts`

Stores the backend host URL.

- **Content**:
  - `backendHost`: Uses environment variable `NEXT_PUBLIC_SKYEGPT_BACKEND_HOST` or defaults to `http://localhost:8000`.

---

### `layout.tsx`

The root layout for the app.

- **Features**:
  - Uses the Poppins font from Google Fonts.
  - Sets metadata (title and description).
  - Applies global CSS.

---

### `page.tsx`

The main page of the app.

- **Features**:
  - Creates a new conversation ID when the page loads.
  - Displays the SkyeGPT logo and images (gears, robot) on desktop.
  - Renders the `ChatBox` component for the chat interface.
  - Includes a footer with a note about verifying answers.

---


