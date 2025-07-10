import { useState, useEffect } from "react";
import styles from "./scroll-top.module.css";

export const ScrollTop = () => {
  const [isVisible, setIsVisible] = useState(false);

  // スクロール位置を監視し、一定以上スクロールしたらボタンを表示
  useEffect(() => {
    const toggleVisibility = () => {
      if (window.pageYOffset > 1) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener("scroll", toggleVisibility);

    // コンポーネントのアンマウント時にイベントリスナーを削除
    return () => window.removeEventListener("scroll", toggleVisibility);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <>
      {isVisible && (
        <button
          onClick={scrollToTop}
          className={styles.scroll_to_top_btn}
          aria-label="ページの先頭へ戻る"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={styles.arrow_icon}
          >
            <path d="m18 15-6-6-6 6" />
          </svg>
        </button>
      )}
    </>
  );
};
