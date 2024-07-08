import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import axios from "axios";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (input.trim() === "") return;
    const userMessage = { sender: "user", text: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    axios
      .get(`${import.meta.env.VITE_API_URL}?message="${input}"`)
      .then((res) => {
        const aiMessage = { sender: "ai", text: res.data.message };
        setMessages((prevMessages) => [...prevMessages, aiMessage]);
      });
    setInput("");
  };

  const handleKeyPress = (e) => {
    if ( e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-70px)]">
      <header className="flex items-center justify-start px-4 py-2 border-b">
        <h1 className="text-lg font-semibold">Chat with docs</h1>
      </header>
      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex items-end space-x-2 ${
              message.sender === "user" ? "justify-end" : ""
            }`}
          >
            {message.sender === "ai" && (
              <Avatar>
                <AvatarImage src="/placeholder-user.jpg" />
                <AvatarFallback>Ai</AvatarFallback>
              </Avatar>
            )}
            <div
              className={`p-2 rounded-lg ${
                message.sender === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-100 dark:bg-gray-800"
              }`}
            >
              <p className="text-sm">{message.text}</p>
            </div>
            {message.sender === "user" && (
              <Avatar>
                <AvatarImage src="/placeholder-user.jpg" />
                <AvatarFallback>U</AvatarFallback>
              </Avatar>
            )}
          </div>
        ))}
      </main>
      <footer className="flex items-center space-x-2 p-2 border-t">
        <Input
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          value={input}
          className="flex-1"
          placeholder="Type a message"
        />
        <Button onClick={sendMessage} variant="outline" size="sm">
          Send
        </Button>
      </footer>
    </div>
  );
}