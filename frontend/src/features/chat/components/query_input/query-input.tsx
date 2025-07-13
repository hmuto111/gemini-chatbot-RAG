import styles from "./query-input.module.css";
import { IoSend } from "react-icons/io5";

type Props = {
  query: string;
  setQuery: (query: string) => void;
};

export const QueryInput = ({ query, setQuery }: Props) => {
  const handleQuerySend = () => {
    console.log("Query sent:", query);
    // apiの処理を書く
    setQuery("");
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
          className={styles.query_area}
          placeholder="Tuna AIへの質問を入力..."
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          value={query}
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
