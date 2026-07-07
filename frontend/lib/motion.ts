import type { Transition, Variants } from "framer-motion";

export const motionTimings = {
  fast: 0.16,
  normal: 0.24,
  slow: 0.32
};

const easeOut: Transition["ease"] = "easeOut";

export const pageMotion = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: motionTimings.normal, ease: easeOut }
};

export const cardMotion = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  whileHover: { y: -3 },
  transition: { duration: motionTimings.normal, ease: easeOut }
};

export const listMotion = {
  initial: "hidden",
  animate: "show",
  variants: {
    hidden: {},
    show: {
      transition: {
        staggerChildren: 0.045
      }
    }
  }
} satisfies { initial: string; animate: string; variants: Variants };

export const itemMotion = {
  variants: {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0 }
  },
  transition: { duration: motionTimings.normal, ease: easeOut }
};

export const toastMotion = {
  initial: { opacity: 0, y: 18, scale: 0.98 },
  animate: { opacity: 1, y: 0, scale: 1 },
  exit: { opacity: 0, y: 12, scale: 0.98 },
  transition: { duration: motionTimings.fast, ease: easeOut }
};
