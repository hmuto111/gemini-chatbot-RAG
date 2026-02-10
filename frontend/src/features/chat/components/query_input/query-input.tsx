import type { chatHistory } from "../../types/chat-history";
import { createResponse } from "../../api/create-response";
import styles from "./query-input.module.css";
import { IoSend } from "react-icons/io5";
import { useRef } from "react";

type Props = {
  sessionId: string | null;
  query: string;
  setQuery: (query: string) => void;
  chatHistory: chatHistory[];
  setChatHistory: (chatHistory: chatHistory[]) => void;
};

export const QueryInput = ({
  sessionId,
  chatHistory,
  setChatHistory,
}: Props) => {
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleQuerySend = async () => {
    const query = inputRef.current?.value || "";

    console.log("Query sent:", query);
    if (!sessionId || !query.trim()) {
      console.error("Session ID or query is missing.");
      return;
    }

    const user_query = query;

    if (inputRef.current) {
      inputRef.current.value = "";
    }

    setChatHistory([...chatHistory, { userQuery: query, aiResponse: "" }]);

    const response = await createResponse({
      session_id: sessionId,
      user_query: user_query,
    });

    setChatHistory([
      ...chatHistory,
      { userQuery: query, aiResponse: response.response },
    ]);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (!e.shiftKey && e.key === "Enter") {
      e.preventDefault();
      handleQuerySend();
    }
  };

  return (
    <div className={styles.query_container}>
      <div className={styles.query_box}>
        <textarea
          ref={inputRef}
          className={styles.query_area}
          placeholder="Tuna AIへの質問を入力..."
          onKeyDown={handleKeyDown}
        />
        <button
          className={styles.query_send}
          title="送信"
          onClick={handleQuerySend}
        >
          <IoSend color="#000080" size="1.5rem" />
        </button>
      </div>
    </div>
  );
};
