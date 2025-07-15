import { useState } from "react";
import { useSession } from "../../hooks/useSession";
import { ChatContent } from "../chat_content/chat-content";
import { QueryInput } from "../query_input/query-input";
import type { chatHistory } from "../../types/chat-history";
import styles from "./chat.module.css";

export const Chat = () => {
  const [query, setQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [chatHistory, setChatHistory] = useState<chatHistory[]>([]);
  const { sessionId } = useSession();

  return (
    <div className={styles.chat_container}>
      <div className={styles.chat_content_wrapper}>
        <ChatContent chatHistory={chatHistory} />
      </div>
      <div className={styles.query_container_wrapper}>
        <QueryInput
          sessionId={sessionId}
          query={query}
          setQuery={setQuery}
          chatHistory={chatHistory}
          setChatHistory={setChatHistory}
        />
      </div>
    </div>
  );
};
