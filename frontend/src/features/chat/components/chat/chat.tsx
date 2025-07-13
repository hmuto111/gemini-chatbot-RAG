import { useState } from "react";

import { ChatContent } from "../chat_content/chat-content";
import { QueryInput } from "../query_input/query-input";
import styles from "./chat.module.css";

export const Chat = () => {
  const [query, setQuery] = useState("");

  return (
    <div className={styles.chat_container}>
      <div className={styles.chat_content_wrapper}>
        <ChatContent />
      </div>
      <div className={styles.query_container_wrapper}>
        <QueryInput query={query} setQuery={setQuery} />
      </div>
    </div>
  );
};
