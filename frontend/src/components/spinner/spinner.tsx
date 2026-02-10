import styles from "./spinner.module.css";

type Props = {
  size: "small" | "medium" | "large";
};

const Spinner = ({ size = "medium" }: Props) => {
  const spinnerClass = `${styles.spinner} ${styles[size]}`;

  return (
    <div className={styles.container}>
      <div className={spinnerClass}></div>
    </div>
  );
};

export default Spinner;
