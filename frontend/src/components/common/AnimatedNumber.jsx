import { useEffect, useState } from "react";

import { motion, useMotionValue, useSpring } from "motion/react";

function AnimatedNumber({
  value,
  decimals = 0,
  suffix = "",
  prefix = "",
  duration = 1.2,
}) {
  const numericValue = Number(value);

  const motionValue = useMotionValue(0);

  const springValue = useSpring(motionValue, {
    stiffness: 70,
    damping: 20,
    duration,
  });

  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    motionValue.set(
      Number.isFinite(numericValue) ? numericValue : 0
    );
  }, [numericValue, motionValue]);

  useEffect(() => {
    const unsubscribe = springValue.on("change", (latest) => {
      setDisplayValue(latest);
    });

    return unsubscribe;
  }, [springValue]);

  const formattedValue = displayValue.toLocaleString("en-IN", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return (
    <motion.span
      style={{
        fontSize: "inherit",
        fontWeight: "inherit",
        lineHeight: "inherit",
        color: "inherit",
        letterSpacing: "inherit",
      }}
    >
      {prefix}
      {formattedValue}
      {suffix}
    </motion.span>
  );
}

export default AnimatedNumber;