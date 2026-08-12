import { useEffect, useRef } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";

// Animates a numeric value counting up to `value` whenever it changes,
// formatted with `format` (defaults to a fixed-2-decimal string).
export default function AnimatedNumber({ value, format, prefix = "", suffix = "" }) {
  const motionValue = useMotionValue(0);
  const spring = useSpring(motionValue, { stiffness: 90, damping: 20, mass: 0.6 });
  const hasMounted = useRef(false);

  useEffect(() => {
    motionValue.set(hasMounted.current ? value : 0);
    hasMounted.current = true;
    const timeout = setTimeout(() => motionValue.set(value), 0);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  const display = useTransform(spring, (v) => `${prefix}${format ? format(v) : Math.round(v)}${suffix}`);

  return <motion.span>{display}</motion.span>;
}
