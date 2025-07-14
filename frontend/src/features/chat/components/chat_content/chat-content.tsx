import styles from "./chat-content.module.css";
import { UserChatMessage, AIChatMessage } from "../chat_message/chat-message";

export const ChatContent = () => {
  return (
    <div className={styles.chat_content}>
      <UserChatMessage content="Hello, how can I help you?" />
      <AIChatMessage
        content={`# I'm looking for information on your services.

\`\`\`json
{
  "example": "data",
  "status": "success"
}
\`\`\`

## Additional Information

This is a sample response with proper formatting.

## Additional Information

This is a sample response with proper formatting.


`}
      />
    </div>
  );
};
