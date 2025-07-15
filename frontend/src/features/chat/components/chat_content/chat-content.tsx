import styles from "./chat-content.module.css";
import { useEffect, useRef } from "react";
import { UserChatMessage, AIChatMessage } from "../chat_message/chat-message";
import type { chatHistory } from "../../types/chat-history";
import { Loading } from "../loading/loading";
import { v4 as uuid } from "uuid";

type Props = {
  chatHistory: chatHistory[];
};

export const ChatContent = ({ chatHistory }: Props) => {
  const chatContentRef = useRef<HTMLDivElement>(null);
  const prevChatHistoryLength = useRef(0);

  useEffect(() => {
    const currentLength = chatHistory.length;
    const hasNewUserMessage = currentLength > prevChatHistoryLength.current;

    if (hasNewUserMessage && chatContentRef.current) {
      chatContentRef.current.scrollTop = chatContentRef.current.scrollHeight;
    }

    prevChatHistoryLength.current = currentLength;
  }, [chatHistory]);

  return (
    <div className={styles.chat_content} ref={chatContentRef}>
      {chatHistory &&
        chatHistory.map((history) => {
          return (
            <div className={styles.chat_message} key={uuid()}>
              <UserChatMessage content={history.userQuery} />
              {history.aiResponse ? (
                <AIChatMessage content={history.aiResponse} />
              ) : (
                <Loading />
              )}
            </div>
          );
        })}
    </div>
  );
};
