import styles from "./chat-message.module.css";
import { MarkdownRender } from "../markdown/markdown-render";

type ChatMessageProps = {
  content: string;
};

export const UserChatMessage = ({ content }: ChatMessageProps) => {
  return <div className={styles.user_chat_message}>{content}</div>;
};

export const AIChatMessage = ({ content }: ChatMessageProps) => {
  return (
    <div className={styles.ai_chat_message}>
      <MarkdownRender content={content} />
    </div>
  );
};
