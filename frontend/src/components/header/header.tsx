import { Link } from "react-router-dom";
import { paths } from "@/config/paths";
import styles from "./header.module.css";
import { Typewriter } from "react-simple-typewriter";

export const Header = () => {
  return (
    <header className={styles.header}>
      <div className={styles.title}>
        <Typewriter
          words={["Tuna AI"]}
          loop={1}
          cursor={false}
          cursorStyle="_"
          typeSpeed={70}
          deleteSpeed={50}
          delaySpeed={1000}
        />
      </div>
    </header>
  );
};
