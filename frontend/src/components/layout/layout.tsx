import type { ReactNode } from "react";
import { Header } from "../header/header";
import styles from "./layout.module.css";

type Props = {
  children: ReactNode;
};

export const Layout = ({ children }: Props) => {
  return (
    <div className={styles.layout}>
      <div className={styles.header_wrap}>
        <Header />
      </div>
      <main className={styles.main}>{children}</main>
    </div>
  );
};
