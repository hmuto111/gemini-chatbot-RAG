import { motion } from "motion/react";
import styles from "./loading.module.css";

export const Loading = () => {
  const bubbles = [
    { cx: 5, cy: 40, r: 5, delay: 0, duration: 1.0, yMove: -20 },
    { cx: 30, cy: 40, r: 5, delay: 0.6, duration: 1.0, yMove: -30 },
    { cx: 55, cy: 40, r: 5, delay: 0.3, duration: 1.0, yMove: -20 },
  ];

  return (
    <div className={styles.loading_container}>
      <span>Tuna AIが回答を生成中...</span>
      <motion.div
        drag
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ display: "flex", justifyContent: "flex-start" }}
      >
        <motion.svg width="100" height="50" viewBox="0 0 50 50">
          {/* 泡のアニメーション */}
          {bubbles.map((bubble, index) => (
            <motion.circle
              key={index}
              cx={bubble.cx}
              cy={bubble.cy}
              r={bubble.r}
              fill="#eaf4ffff"
              opacity="0.6"
              animate={{
                y: [0, bubble.yMove],
                opacity: [0.7, 0],
                scale: [1, 2],
              }}
              transition={{
                duration: bubble.duration,
                repeat: Infinity,
                ease: "easeOut",
                delay: bubble.delay,
              }}
            />
          ))}
        </motion.svg>
      </motion.div>
    </div>
  );
};
